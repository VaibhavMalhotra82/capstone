import os
import re
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from prompts import advisory_prompt
from backend.utils import vector_store
from qdrant_client.http import models as rest
from backend.log import logger
from config import MODEL
from models import FinancialState
from langsmith import traceable
from langchain_core.runnables import RunnablePassthrough
load_dotenv()

llm = ChatOpenAI(model=MODEL, api_key=os.getenv('OPENAI_API_KEY')).with_structured_output(FinancialState, include_raw=True)

SUPPORTED_INTENTS = {"loan_inquiry", "investment_advice", "policy_lookup", "general_faq", "human_handoff"}


def _infer_retrieval_intent(query: str, intent: str | None) -> str:
    normalized_intent = intent.strip() if isinstance(intent, str) else None
    if normalized_intent in SUPPORTED_INTENTS:
        return normalized_intent

    lowered = query.lower()
    if re.search(r"\b(loan|mortgage|emi|down payment|eligib|property)\b", lowered):
        return "loan_inquiry"
    if re.search(r"\b(invest|sip|mutual fund|retire|wealth|return)\b", lowered):
        return "investment_advice"
    if re.search(r"\b(policy|fee|charge|penalt|terms?)\b", lowered):
        return "policy_lookup"
    if re.search(r"\b(contact|support|branch|hours?|location|holiday|saturdays?|working day|open|closed)\b", lowered):
        return "general_faq"
    return "general_faq"

@tool
@traceable(run_type="retriever")
async def advisory_engine(query: str, intent: str | None = None) -> dict:
    """Use for banking guidance, eligibility, documentation, rates, policies, down payments, and contact/help questions."""
    try:
        source_documents = []
        query = query.strip()
        retrieval_intent = _infer_retrieval_intent(query, intent)
        logger.log_info("Advisory engine retrieval intent: %s" % (retrieval_intent,))
        formatted_prompt = advisory_prompt.format(intent=retrieval_intent, context="{context}")

        advisory_prompt_template = ChatPromptTemplate.from_messages([('system', formatted_prompt), ('human', " {input}")])

        dynamic_retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 5,
                "filter": rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="metadata.category",
                            match=rest.MatchValue(value=retrieval_intent)
                        )
                    ]
                )
            }
        )

        def format_docs(docs):
            for doc in docs:
                logger.log_info("Retrieved chunk from %s (page %s):" % (doc.metadata.get('source', 'unknown'), doc.metadata.get('page', 'unknown')))
                source_documents.append(
                {
                "source": doc.metadata.get('source', 'unknown'),
                "page": doc.metadata.get('page', 'unknown'),
                "content": doc.page_content,
                }
                )
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {
                "context": dynamic_retriever | format_docs,
                "input": RunnablePassthrough(),
                "intent": lambda x: retrieval_intent
            }
            | advisory_prompt_template
            | llm
        )

        result = await rag_chain.ainvoke(query)
        logger.log_info(f"Advisory engine result: {result}")

        if not source_documents:
            result_dict = {"advice": "No information found in the knowledge base."}
        elif isinstance(result, dict) and hasattr(result.get("parsed"), "advice"):
            result_dict = {"advice": result["parsed"].advice}
        elif hasattr(result, "advice"):
            result_dict = {"advice": result.advice}
        elif hasattr(result, "dict"):
            result_dict = result.dict()
        else:
            result_dict = {"advice": str(result)}

        '''docs = await dynamic_retriever.ainvoke(query)
        source_documents = [
            {
                "source": doc.metadata.get('source', 'unknown'),
                "page": doc.metadata.get('page', 'unknown'),
                "content": doc.page_content,
            }
            for doc in docs
        ]'''

        return {
            "result": result_dict,
            "source_documents": source_documents
        }
    except Exception as e:
        import traceback
        logger.log_error("Advisory engine exception: %s\n%s" % (e, traceback.format_exc()))
        raise
