import atexit
import os
import uuid
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
from config import VECTOR_DB_PATH, DIMENSIONS
from backend.log import logger

load_dotenv()

_qdrant_closed = False

# 1. Initialize Qdrant in Local Persistent Mode
qdrant_client = QdrantClient(path=VECTOR_DB_PATH, prefer_grpc=True)  # prefer_grpc can speed up local operations
collection_name = "XYZ_banking_policies"

if not qdrant_client.collection_exists(collection_name=collection_name):
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=DIMENSIONS, distance=models.Distance.COSINE),
    )

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=DIMENSIONS)

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
    embedding=embeddings,
)


def close_qdrant_client():
    """Close the shared Qdrant client exactly once, before interpreter teardown."""
    global _qdrant_closed
    if _qdrant_closed:
        return

    try:
        qdrant_client.close()
        logger.log_info("Qdrant client closed successfully.")
    except ImportError:
        # Interpreter shutdown may already be in progress; keep teardown quiet.
        pass
    except Exception as e:
        logger.log_warning(f"Failed to close Qdrant client cleanly: {e}")
    finally:
        _qdrant_closed = True


def cleanup_session_artifacts(session_id: str):
    """Delete per-session history and feedback files."""
    for prefix in ("history", "feedback"):
        file_path = f"{prefix}_{session_id}.json"
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.log_info(f"Removed session artifact: {file_path}")
        except Exception as e:
            logger.log_warning(f"Failed to remove session artifact {file_path}: {e}")


atexit.register(close_qdrant_client)

def generate_session_id():
    """Generate a deterministic machine-scoped user id."""
    try:
        raw = uuid.uuid4().hex  # Generate a random UUID and get its hex representation
        return raw
    except Exception as e:
        logger.log_error(f"Error generating session ID: {e}")
        return "unknown_session"
