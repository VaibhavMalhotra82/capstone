from log import Logger
import asyncio
from intent_classifier import categorize_intent
from advisory_engine import advisory_engine
from utils import qdrant_client
from config import DISCLAIMER

logger = Logger(log_file="app.log")

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
    
    # 3. For simplicity, we are directly calling the advisory engine here.
    advisory_engine_result = await advisory_engine(user_query, intent_result['intent'], logger)
    logger.log_info("Advisory engine response: %s" %(advisory_engine_result))
    return advisory_engine_result.advice + "\n\n" + DISCLAIMER
    
async def main():
    while True:
        user_query = await input_user_query()
        if user_query.lower() in ["exit", "quit"]:
            logger.log_info("User requested to %s." %(user_query.lower()))
            print("Thank you for using XYZ bank chatbot. Have a great day!")
            qdrant_client.close()  # Ensure we close the client after processing
            break
        response = await process_query(user_query)
        logger.log_info("Bot response: %s" %(response))
        print(f"\n{response}")
        print("=="*50)

if __name__ == "__main__":
    logger.log_info("XYZ Bank Chatbot initialized and ready to receive queries.")    
    asyncio.run(main())
