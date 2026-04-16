import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables import RunnablePassthrough
from log import Logger
from dotenv import load_dotenv
from models import FinancialState
from prompts import advisory_prompt

from config import TOP_K, MODEL
from utils import vector_store
from qdrant_client.http import models as rest

load_dotenv()

# This tells the LLM it is ALLOWED to output a JSON blob for these tools.

llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPENAI_API_KEY")).with_structured_output(FinancialState)

async def advisory_engine(query: str, intent: str, logger: Logger) -> dict:
    """
    Generates the final response using retrieved documents and UI tools.
    """
    # 1. Construct the context-heavy prompt
    formatted_prompt  = advisory_prompt.format(intent=intent, context="{context}")

    # 2. Prepare the messages for the LLM
    query = query.strip()
    #advisory_prompt_template = ChatPromptTemplate.from_messages([SystemMessage(content=formatted_prompt), HumanMessage(content=query)])
    advisory_prompt_template = ChatPromptTemplate.from_messages([('system', formatted_prompt), ('human', " {input}")])

    # 3. This creates the dynamic retriever with the appropriate filter based on the intent
    dynamic_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
                    "k": TOP_K,
                    "filter": rest.Filter(
                        must=[
                            rest.FieldCondition(
                                key="metadata.category", 
                                match=rest.MatchValue(value=intent)
                            )
                        ]
                    )
                }
        )

    # 4. Define a helper to format documents into a single string
    def format_docs(docs):
        for doc in docs:
            logger.log_info("Retrieved chunk from %s (page %s):" %(doc.metadata['source'], doc.metadata['page']))
        return "\n\n".join(doc.page_content for doc in docs)
    
    # 5. Build the RAG chain (LCEL)
    rag_chain = (
        {
            "context": dynamic_retriever | format_docs,  # Use your filtered retriever here
            "input": RunnablePassthrough(),      # Passes the query straight through
            "intent": lambda x: intent           # Passes the intent string
        }
        | advisory_prompt_template               # Your template with {context}, {input}, {intent}
        | llm                         # The LLM that outputs FinancialState
    )

    # 6. Invoke the chain
    # This will return a FinancialState object directly!
    return rag_chain.invoke(query)
