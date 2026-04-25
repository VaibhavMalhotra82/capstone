import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils import vector_store, qdrant_client
from config import CHUNK_SIZE, CHUNK_OVERLAP

def ingest_bank_data(pdf_files_config):
    """
    pdf_files_config: A list of dicts like:
    [{'path': 'docs/savings.pdf', 'category': 'savings'}, ...]
    """
    
    # 1. Initialize the Text Splitter
    # chunk_overlap ensures that context isn't cut off at the edges of a chunk
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )
    
    all_chunks = []

    for file_info in pdf_files_config:
        print(f"Processing {file_info['path']}...")
        
        # 2. Load the PDF
        loader = PyPDFLoader(file_info['path'])
        pages = loader.load()
        
        # 3. Split into chunks
        chunks = text_splitter.split_documents(pages)
        
        # 4. Enrich metadata
        # PyPDFLoader automatically adds 'source' and 'page'
        # We manually add 'category' for the Qdrant filtering
        for chunk in chunks:
            chunk.metadata["category"] = file_info['category']
        
        all_chunks.extend(chunks)

    # 5. Push to Qdrant
    vector_store.add_documents(documents=all_chunks)
    print(f"Success! Ingested {len(all_chunks)} chunks from {len(pdf_files_config)} files.")

if __name__ == "__main__":
    # Run once to prime the vector DB
    bank_docs = [
        {"path": "rag_data/investment_guide.pdf", "category": "investment_advice"},
        {"path": "rag_data/loan.pdf", "category": "loan_inquiry"},
        {"path": "rag_data/faqs.pdf", "category": "general_faq"},
        {"path": "rag_data/policy.pdf", "category": "policy_lookup"},
    ]
    ingest_bank_data(bank_docs)
    qdrant_client.close()