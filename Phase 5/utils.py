from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
from config import VECTOR_DB_PATH, DIMENSIONS

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
