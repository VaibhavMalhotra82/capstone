import os
import asyncio
from backend.memory import load_history, save_history_with_guardrail
from backend.intent_classifier import categorize_intent
from backend.advisory_engine import advisory_engine
from tools import calculate_emi, calculate_sip
from prompts import agent_prompt
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from config import MODEL, GUARDRAILS_CHECK
from guardrails import pre_check
from langchain_core.messages import HumanMessage, AIMessage
from backend.feedback import store_feedback, load_feedback
from backend.log import logger, UIAgentCallbackHandler
from langsmith import traceable
from observability import time_it
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPENAI_API_KEY"), streaming=True)


def _needs_sip(query: str) -> bool:
    lowered = query.lower()
    sip_markers = [
        "save",
        "saving",
        "savings",
        "sip",
        "invest",
        "investment",
        "monthly",
        "per month",
        "future value",
        "reaches",
    ]
    return any(marker in lowered for marker in sip_markers)


def _needs_loan_advisory(query: str, intent: str) -> bool:
    if intent != "loan_inquiry":
        return False
    lowered = query.lower()
    advisory_markers = [
        "down payment",
        "home loan",
        "loan",
        "eligible",
        "eligibility",
        "can i use",
        "enough",
        "requirement",
        "required",
    ]
    return any(marker in lowered for marker in advisory_markers)


def _needs_grounded_advisory(query: str, intent: str) -> bool:
    if intent in {"general_faq", "policy_lookup", "human_handoff"}:
        return True

    lowered = query.lower()
    grounded_markers = [
        "branch",
        "hour",
        "timing",
        "location",
        "contact",
        "support",
        "holiday",
        "saturday",
        "working day",
        "open",
        "closed",
        "fee",
        "charge",
        "policy",
        "terms",
    ]
    return any(marker in lowered for marker in grounded_markers)


def _build_advisory_query(user_query: str) -> str:
    lowered = user_query.lower()
    if "down payment" in lowered and "home loan" in lowered:
        return "down payment requirements for a home loan"
    if "home loan" in lowered:
        return "home loan eligibility, requirements, and down payment guidance"
    return user_query


def _knowledge_unavailable_message(intent: str) -> str:
    if intent == "policy_lookup":
        return "The requested policy detail is not available in the knowledge base."
    if intent == "human_handoff":
        return "The requested contact detail is not available in the knowledge base."
    return "The requested branch or working-hours detail is not available in the knowledge base."

@time_it
@traceable(run_type="chain")
async def process_query(user_query: str, session_id: str, callbacks=None) -> dict:
    if GUARDRAILS_CHECK:
        allowed, reason = pre_check(user_query)
        if not allowed:
            logger.log_warning("Guardrail pre-check failed: %s" % (reason,))
            return {
                "response_text": f"Your query cannot be processed: {reason}",
                "intent": {"intent": "guardrail_blocked", "confidence_score": 1.0},
                "source_documents": [],
                "agent_feedback": [],
                "scratchpad": "",
            }

    intent_result = await categorize_intent(user_query)
    logger.log_info("Intent classification result: %s" % (intent_result,))

    if intent_result['confidence_score'] < 0.7:
        logger.log_warning("Low confidence in intent classification: %s" % (intent_result,))
        return {
            "response_text": "I'm sorry, I couldn't understand your query. Could you please rephrase it?",
            "intent": intent_result,
            "source_documents": [],
            "agent_feedback": [],
            "scratchpad": "",
        }

    if intent_result['intent'] == "feedback" and intent_result.get('feedback'):
        logger.log_info("Storing user feedback: %s" % (intent_result['feedback'],))
        store_feedback(session_id, [intent_result['feedback']])

    try:
        history = load_history(session_id)
        feedback_messages = load_feedback(session_id)
        advisory_context = "No pre-fetched advisory context."
        prefetched_source_documents = []
        should_prefetch_mixed_advisory = _needs_loan_advisory(user_query, intent_result["intent"]) and _needs_sip(user_query)
        should_prefetch_grounded_advisory = _needs_grounded_advisory(user_query, intent_result["intent"])
        should_prefetch_advisory = should_prefetch_mixed_advisory or should_prefetch_grounded_advisory

        if should_prefetch_advisory:
            advisory_query = _build_advisory_query(user_query) if should_prefetch_mixed_advisory else user_query
            logger.log_info(
                "Pre-fetching advisory guidance with intent %s: %s"
                % (intent_result["intent"], advisory_query)
            )
            advisory_result = await advisory_engine.ainvoke(
                {"query": advisory_query, "intent": intent_result["intent"]}
            )
            advisory_payload = advisory_result.get("result", {}) if isinstance(advisory_result, dict) else {}
            prefetched_source_documents = advisory_result.get("source_documents", []) if isinstance(advisory_result, dict) else []
            if should_prefetch_grounded_advisory and not prefetched_source_documents:
                advisory_context = _knowledge_unavailable_message(intent_result["intent"])
            else:
                advisory_context = advisory_payload.get("advice", str(advisory_payload))

        tools = [calculate_emi, calculate_sip] if should_prefetch_advisory else [advisory_engine, calculate_emi, calculate_sip]
        agent_prompt_formatted = agent_prompt.replace("{intent}", intent_result['intent'])

        prompt = ChatPromptTemplate.from_messages([
            ("system", agent_prompt_formatted),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
            MessagesPlaceholder("agent_feedback", optional=False),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)
        callback_handler = UIAgentCallbackHandler()
        executor_callbacks = [callback_handler]
        if callbacks:
            executor_callbacks.extend(callbacks)

        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            callbacks=executor_callbacks,
            verbose=False,
            max_iterations=5,
            return_intermediate_steps=True,
        )

        args = {
            "input": user_query,
            "chat_history": history,
            "agent_feedback": feedback_messages,
            "advisory_context": advisory_context,
        }

        response = await agent_executor.ainvoke(args)
        response_text = response.get('output') if isinstance(response, dict) else str(response)
        intermediate_steps = response.get('intermediate_steps', []) if isinstance(response, dict) else []

        def _extract_source_documents(observation):
            if isinstance(observation, dict):
                if observation.get('source_documents'):
                    return observation['source_documents']
                result_value = observation.get('result')
                if isinstance(result_value, dict) and result_value.get('source_documents'):
                    return result_value['source_documents']
            return None

        scratchpad_entries = []
        for step in intermediate_steps:
            try:
                action, observation = step
                tool_name = getattr(action, 'tool', str(action))
                tool_input = getattr(action, 'tool_input', None)
                scratchpad_entries.append(f"{tool_name}({tool_input}) -> {observation}")
            except Exception:
                scratchpad_entries.append(str(step))

        scratchpad = "\n\n".join(scratchpad_entries)
        source_documents = callback_handler.source_documents or prefetched_source_documents
        if not source_documents:
            for step in intermediate_steps:
                try:
                    _, observation = step
                except Exception:
                    continue
                extracted = _extract_source_documents(observation)
                if extracted:
                    source_documents = extracted
                    break

        if not source_documents and isinstance(response, dict) and response.get('source_documents'):
            source_documents = response['source_documents']

        agent_feedback_text = [msg.content if hasattr(msg, 'content') else str(msg) for msg in feedback_messages]

        history.append(HumanMessage(content=user_query.encode('utf-8')))
        history.append(AIMessage(content=response_text.encode('utf-8') if isinstance(response_text, str) else str(response_text)))
        save_history_with_guardrail(session_id, history)

        return {
            "response_text": response_text,
            "intent": intent_result,
            "source_documents": source_documents,
            "agent_feedback": agent_feedback_text,
            "scratchpad": scratchpad,
        }
    except Exception as e:
        import traceback
        logger.log_error(f"Error during agent execution: {e}\n{traceback.format_exc()}")
        return {
            "response_text": "An error occurred while processing your request. Please try again later.",
            "intent": intent_result,
            "source_documents": [],
            "agent_feedback": [],
            "scratchpad": "",
        }


def process_query_sync(user_query: str, session_id: str, callbacks=None) -> dict:
    return asyncio.run(process_query(user_query, session_id, callbacks=callbacks))
