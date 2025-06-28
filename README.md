# RAG-Based FAQ Chatbot with FastAPI and Weaviate

This project is a Retrieval-Augmented Generation (RAG) chatbot designed to answer FAQ-style questions using a combination of semantic search and LLMs. The backend is built with FastAPI and leverages Weaviate for vector-based document storage and retrieval.

## Features

- **FastAPI** backend for serving RESTful endpoints
- **Weaviate** cloud vector DB for storing and querying document embeddings
- **SentenceTransformers** to embed and match user queries
- **Swagger UI** auto-generated for testing endpoints
- **JSON-based FAQ ingestion and scraping pipeline**

## Project Structure

```
├── app.py                  # FastAPI main entrypoint
├── faq_api.py              # Flask-style script for local testing
├── faq_data.json           # Preprocessed FAQs
├── faq_rag_demo.py         # Offline retrieval-augmented QA demo
├── query_weaviate.py       # Utility to search queries on Weaviate
├── requirements.txt        # Python dependencies
├── scrape_faq.py           # Web scraper for FAQ generation
├── upload_to_weaviate.py   # Script to push data to Weaviate
├── README.md               # Documentation
└── Procfile                # For deployment (e.g., on Railway/Heroku)
```

## How It Works

1. **Data Prep**: Raw FAQ content is scraped and structured into `faq_data.json`.
2. **Vectorization**: The content is embedded via SentenceTransformer and uploaded to Weaviate.
3. **Querying**: User question is embedded and compared against stored embeddings for top match.
4. **Response**: The answer(s) with highest cosine similarity are returned via the `/ask` endpoint.

## Setup

1. **Clone the repository**:
```bash
git clone https://github.com/incyvincy/WebopsSumCH24B050AIRAG.git
cd WebopsSumCH24B050AIRAG
```

2. **Create and activate a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run FastAPI server**:
```bash
uvicorn app:app --reload
```

5. **Access Swagger UI**:
Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

## Environment Variables
Create a `.env` file or export these:
```env
WEAVIATE_URL="<your_weaviate_instance_url>"
my-webops-api-key-weaviate="<your_api_key>"
```

## Example Request
```json
POST /ask
{
  "question": "What is Electrical Engineering?"
}
```

## Authors
- CH24B050 – AIRAG

---
**Note:** This project is academic and experimental in nature.
