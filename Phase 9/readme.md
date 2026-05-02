## Installation steps

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_api_key
```

---

## PDF Ingestion (One-Time Step)

This step converts PDFs into vector embeddings.

```bash
python ingest.py
```

What this does:

* Loads all PDFs from `rag_data/`
* Splits them into semantic chunks
* Generates embeddings using OpenAI
* Stores vectors locally using Qdrant

---

## Running the agent

```bash
python -m streamlit run ui\streamlit_app.py
```

---

## Output files

* app.log
  * Contins the application logs
* history_<session_id>.json
  * Contains the session based history
* feedback_<session_id>.json
  * Contains the session based feedback

---

## Git repo public (Phase wise)

* https://github.com/VaibhavMalhotra82/capstone
