import json
import os
import pandas as pd

# 1. Qdrant & Vector Store Imports
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore

# 2. OpenAI & LangChain Imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# 3. RAGAS & Data Imports
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset

# 4. OpenAI API Key Setup and configurations
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from config import MODEL, DIMENSIONS, VECTOR_DB_PATH

# --- CONFIGURATION ---
# Ensure your OPENAI_API_KEY is set in your environment variables
HISTORY_FILE = "history_8a1e434dbbde4ab0bff7653aabba2e95.json"
COLLECTION_NAME = "XYZ_banking_policies"

# --- 1. INITIALIZE CLIENTS ---
def get_vector_store():
    client = QdrantClient(path=VECTOR_DB_PATH, prefer_grpc=True)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=DIMENSIONS)
    return QdrantVectorStore(
        client=client, 
        collection_name=COLLECTION_NAME, 
        embedding=embeddings
    )

# --- 2. DATA PREPARATION ---
def prepare_eval_dataset(file_path, vector_store):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None

    with open(file_path, 'r') as f:
        data = json.load(f)

    questions = []
    answers = []
    contexts = []

    # Iterate through the specific nested JSON structure
    for i in range(len(data) - 1):
        current_msg = data[i]
        next_msg = data[i+1]
        
        # Identify Human-AI pairs
        if current_msg["type"] == "human" and next_msg["type"] == "ai":
            # Extract nested content strings
            q_text = current_msg["data"]["content"]
            a_text = next_msg["data"]["content"]
            
            # Re-retrieve context from Qdrant for this specific question
            retrieved_docs = vector_store.similarity_search(q_text, k=2)
            context_list = [doc.page_content for doc in retrieved_docs]
            
            questions.append(q_text)
            answers.append(a_text)
            contexts.append(context_list)

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts
    })

# --- 3. RUN EVALUATION ---
def run_quality_check():
    # Setup
    vs = get_vector_store()
    dataset = prepare_eval_dataset(HISTORY_FILE, vs)
    
    if dataset:
        # Initialize the Judge
        judge_llm = ChatOpenAI(model=MODEL)
        
        # Execute Ragas Evaluation
        print(f"🚀 Running evaluation on {len(dataset)} conversation turns...")
        results = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy],
            llm=judge_llm
        )
        
        # Output Results
        df = results.to_pandas()
        df.to_csv("banking_quality_report.csv", encoding='utf-8', index=False)
        print("\n✅ Report Generated: banking_quality_report.csv")
        print(df[['user_input', 'faithfulness', 'answer_relevancy']])

if __name__ == "__main__":
    run_quality_check()