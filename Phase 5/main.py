import os
from log import logger, LoggingCallbackHandler
import asyncio
from intent_classifier import categorize_intent
from advisory_engine import advisory_engine
from utils import qdrant_client
from config import DISCLAIMER
from tools import calculate_emi, calculate_sip
from prompts import agent_prompt
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from config import MODEL

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPENAI_API_KEY"))

#logger = Logger(log_file="app.log")

async def input_user_query() -> str:
    user_query = input("Welcome to XYZ bank! How can I assist you today?\n")
    logger.log_info("User query: %s" % user_query)
    return user_query

async def process_query(user_query: str) -> str:
    # 1. Classify the intent of the query
    intent_result = await categorize_intent(user_query)

    logger.log_info("Intent classification result: %s" %(intent_result))

    # 2. Based on the intent generate advice
    if intent_result['confidence_score'] < 0.7:
        logger.log_warning("Low confidence in intent classification: %s" %(intent_result))
        return "I'm sorry, I couldn't understand your query. Could you please rephrase it?"
    
    # 3. Agent execution with tools and RAG

    tools = [advisory_engine, calculate_emi, calculate_sip]

    agent_prompt_formatted = agent_prompt.replace("{intent}", intent_result['intent'])
    # NOTE: The 'agent_scratchpad' is mandatory for LangChain Agents
    prompt = ChatPromptTemplate.from_messages([
        ("system", agent_prompt_formatted), # Use your existing persona prompt
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"), 
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    callback_handler = LoggingCallbackHandler()
    agent_executor = AgentExecutor(agent=agent, tools=tools, callbacks=[callback_handler], verbose=False, max_iterations=5)
    try:
        response = await agent_executor.ainvoke({"input": user_query})
        return response
    except Exception as e:
        import traceback
        logger.log_error(f"Error during agent execution: {e}\n{traceback.format_exc()}")
        return "An error occurred while processing your request. Please try again later."

async def main():
    while True:
        user_query = await input_user_query()
        if user_query.lower() in ["exit", "quit"]:
            logger.log_info("User requested to %s." %(user_query.lower()))
            print("Thank you for using XYZ bank chatbot. Have a great day!")
            qdrant_client.close()  # Ensure we close the client after processing
            break
        response = await process_query(user_query)
        final_response = response['output'] if isinstance(response, dict) else response
        #logger.log_info("Bot response: %s" % final_response)
        print(f"\n{final_response}")
        print("=="*50)

if __name__ == "__main__":
    logger.log_info("XYZ Bank Chatbot initialized and ready to receive queries.")    
    asyncio.run(main())
