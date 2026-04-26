import os
from memory import load_history, save_history_with_guardrail
from log import logger, LoggingCallbackHandler
import asyncio
from intent_classifier import categorize_intent
from advisory_engine import advisory_engine
from utils import qdrant_client, generate_session_id
from tools import calculate_emi, calculate_sip
from prompts import agent_prompt
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from config import MODEL, GUARDRAILS_CHECK
from langchain_core.messages import HumanMessage, AIMessage
from feedback import store_feedback, load_feedback
from langsmith import traceable
from observability import time_it

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPENAI_API_KEY"))

async def input_user_query() -> str:
    user_query = input("Welcome to XYZ bank! How can I assist you today?\n")
    logger.log_info("User query: %s" % user_query)
    return user_query

@time_it
@traceable(run_type="chain")
async def process_query(user_query: str, session_id: str) -> str:
    # 1. Classify the intent of the query
    intent_result = await categorize_intent(user_query)

    logger.log_info("Intent classification result: %s" %(intent_result))

    # 2. Based on the confidence score, decide whether to proceed or ask for clarification
    if intent_result['confidence_score'] < 0.7:
        logger.log_warning("Low confidence in intent classification: %s" %(intent_result))
        return "I'm sorry, I couldn't understand your query. Could you please rephrase it?"
    
    # 3. If the intent is feedback, store it and return an acknowledgment
    if intent_result['intent'] == "feedback" and intent_result.get('feedback'):
        logger.log_info("Storing user feedback: %s" %(intent_result['feedback']))
        feedback_response = store_feedback(session_id, [intent_result['feedback']])

    # 3. Agent execution with tools and RAG

    tools = [advisory_engine, calculate_emi, calculate_sip]

    agent_prompt_formatted = agent_prompt.replace("{intent}", intent_result['intent'])
    # NOTE: The 'agent_scratchpad' is mandatory for LangChain Agents
    prompt = ChatPromptTemplate.from_messages([
        ("system", agent_prompt_formatted), # Use your existing persona prompt
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
        MessagesPlaceholder("agent_feedback", optional=False),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    # The LoggingCallbackHandler will log all interactions with the agent, including tool calls and LLM responses. This is crucial for debugging and understanding the agent's behavior.
    callback_handler = LoggingCallbackHandler()

    # The max_iterations parameter is a safety guard to prevent infinite loops in case of unexpected behavior. Adjust as needed.
    agent_executor = AgentExecutor(agent=agent, tools=tools, callbacks=[callback_handler], verbose=False, max_iterations=5)
    try:
        history = load_history(session_id)

        feedback = load_feedback(session_id)

        args = {"input": user_query, "chat_history": history, "agent_feedback": feedback}

        response = await agent_executor.ainvoke(args)

        # Save the updated history after processing the query
        history.append(HumanMessage(content=user_query.encode('utf-8')))
        history.append(AIMessage(content=response['output'].encode('utf-8') if isinstance(response, dict) else response))
        save_history_with_guardrail(session_id, history)

        return response
    except Exception as e:
        import traceback
        logger.log_error(f"Error during agent execution: {e}\n{traceback.format_exc()}")
        return "An error occurred while processing your request. Please try again later."

async def main(session_id: str):
    while True:
        user_query = await input_user_query()

        if GUARDRAILS_CHECK:
            from guardrails import pre_check
            allowed, reason = pre_check(user_query)
            if not allowed:
                logger.log_warning(f"Guardrail pre-check failed: {reason}")
                print(f"\nYour query cannot be processed: {reason}")
                print("=="*50)
                continue
        
        if user_query.lower() in ["exit", "quit"]:
            logger.log_info("User requested to %s." %(user_query.lower()))
            print("Thank you for using XYZ bank chatbot. Have a great day!")
            qdrant_client.close()  # Ensure we close the client after processing
            break
        response = await process_query(user_query, session_id)
        final_response = response['output'] if isinstance(response, dict) else response
        #logger.log_info("Bot response: %s" % final_response)
        print(f"\n{final_response}")
        print("=="*50)

if __name__ == "__main__":
    logger.log_info("XYZ Bank Chatbot initialized and ready to receive queries.")
    session_id = generate_session_id()
    logger.log_info(f"Session ID: {session_id}")    
    asyncio.run(main(session_id))
