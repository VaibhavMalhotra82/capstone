import os

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from models import IntentTag
from langchain_core.messages import SystemMessage, HumanMessage
from prompts import intent_prompt
from config import MODEL

load_dotenv()


# Initialize LLM with structured output
llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPENAI_API_KEY")).with_structured_output(IntentTag)

async def categorize_intent(query: str) -> dict:
    # 1. Get the query.
    query = query.strip()
    
    # 2. Ask the LLM to categorize it.
    messages = [SystemMessage(content=intent_prompt), HumanMessage(content=f"Categorize this banking query: {query}")]
    result = await llm.ainvoke(messages)
    
    # 3. Return the intent and confidence score.
    return {
        "intent": result.category,
        "confidence_score": result.confidence
    }