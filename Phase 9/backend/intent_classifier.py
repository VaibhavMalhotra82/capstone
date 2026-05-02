import os
from models import IntentTag
from prompts import intent_prompt
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from config import MODEL
from backend.log import logger
from langsmith import traceable
from observability import time_it
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPENAI_API_KEY")).with_structured_output(IntentTag, include_raw=True)

@time_it
@traceable(run_type="llm")
async def categorize_intent(query: str) -> dict:
    try:
        query = query.strip()
        messages = [SystemMessage(content=intent_prompt), HumanMessage(content=f"Categorize this banking query: {query}")]
        result = await llm.ainvoke(messages)

        result_dict_raw = result.get('raw', 'No raw output')
        logger.log_info("Intent classification raw output: %s" % (result_dict_raw))
        result_dict_parsed = result.get('parsed', 'No parsed output')
        logger.log_info("Intent classification parsed output: %s" % (type(result_dict_parsed)))

        return {
            "intent": result_dict_parsed.category,
            "confidence_score": result_dict_parsed.confidence,
            "feedback": result_dict_parsed.feedback
        }
    except Exception as e:
        logger.log_error("Error during intent classification: %s" % (str(e)))
        return {
            "intent": "unknown",
            "confidence_score": 0.0,
            "feedback": None
        }
