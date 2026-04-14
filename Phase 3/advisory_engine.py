import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from models import FinancialState
from prompts import advisory_prompt

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")).with_structured_output(FinancialState)

def advisory_engine(query: str, intent: str) -> dict:
    """
    Generates the final response using retrieved documents and UI tools.
    """
    # 1. Construct the context-heavy prompt
    formatted_prompt  = advisory_prompt.format(intent=intent)

    # 2. Prepare the messages for the LLM
    query = query.strip()
    advisory_prompt_template = ChatPromptTemplate.from_messages([SystemMessage(content=formatted_prompt), HumanMessage(content="{query}")])
    
    # 3. Invoke the LLM
    response = llm.invoke(advisory_prompt_template.format(query=query))
    
    # 4. Return the AI message
    return response
