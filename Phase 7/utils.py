import platform
import uuid
import hashlib
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
from config import VECTOR_DB_PATH, DIMENSIONS

from log import logger

load_dotenv()

# 1. Initialize Qdrant in Local Persistent Mode
# This creates a folder named 'bank_db' in your project directory
qdrant_client = QdrantClient(path=VECTOR_DB_PATH, prefer_grpc=True)  # prefer_grpc can speed up local operations
collection_name = "XYZ_banking_policies"

if not qdrant_client.collection_exists(collection_name=collection_name):
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=DIMENSIONS, distance=models.Distance.COSINE),
    )

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=DIMENSIONS) # Ensure OPENAI_API_KEY is in your environment

# 2. Setup the Vector Store
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
    embedding=embeddings,
)

def generate_session_id():
    """Generate a deterministic machine-scoped user id.

    This uses the host node name and the MAC (via uuid.getnode()), hashed
    to produce a stable, non-revealing identifier for logs/metrics.
    """
    try:
        node = platform.node() or ""
        mac = uuid.getnode() or 0
        raw = f"{node}-{mac}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    except Exception as e:
        logger.log_error(f"Error generating session ID: {e}")
        return "unknown_session"