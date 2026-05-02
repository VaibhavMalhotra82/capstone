import json
import os
from log import logger
from config import MODEL
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import messages_to_dict, messages_from_dict, SystemMessage

load_dotenv()

llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPENAI_API_KEY"))

def load_history(session_id: str):
    file_path = f"history_{session_id}.json"
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        dict_history = json.load(f)
    return messages_from_dict(dict_history)

def save_history(session_id: str, messages: list):
    file_path = f"history_{session_id}.json"
    dict_history = messages_to_dict(messages)
    with open(file_path, "w+") as f:
        json.dump(dict_history, f)

def check_history_bloat(session_id: str, limit_kb: int = 100):
    file_path = f"history_{session_id}.json"
    if not os.path.exists(file_path):
        return False
    
    # Get size in bytes, convert to KB
    file_size_kb = os.path.getsize(file_path) / 1024
    return file_size_kb > limit_kb

def summarize_and_prune(messages: list):
    """Summarizes the first 50% and keeps the last 50% raw."""
    midpoint = len(messages) // 2
    old_messages = messages[:midpoint]
    new_messages = messages[midpoint:]
    
    # Prompt the LLM to create a persistent memory block
    summary_prompt = f"Summarize the key banking topics, loan amounts, and user preferences discussed here: {old_messages}"
    summary = llm.invoke(summary_prompt).content
    
    # Combine the summary as a SystemMessage + the fresh messages
    compressed_history = [SystemMessage(content=f"Previous Context Summary: {summary}")]
    compressed_history.extend(new_messages)
    
    return compressed_history

def save_history_with_guardrail(session_id, history):
    # 1. Check if the file is getting too large
    if check_history_bloat(session_id, limit_kb=100):
        logger.log_info(f"Memory bloat detected for {session_id}. Triggering reduction.")
        
        # 2. Choose your strategy: Pruning or Summarizing
        history = summarize_and_prune(history)
        
    # 3. Save the managed history
    save_history(session_id, history)