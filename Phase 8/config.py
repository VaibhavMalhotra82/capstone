import os
from dotenv import load_dotenv

load_dotenv()

# Chat model
MODEL = "gpt-4o-mini"

# Ingestion / retrieval
TOP_K = int(os.getenv("TOP_K", "4"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./bank_db")
DIMENSIONS = int(os.getenv("DIMENSIONS", "512"))

# OpenAI base
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "")

# Guardrails
GUARDRAILS_CHECK = os.getenv("GUARDRAILS_CHECK", True)