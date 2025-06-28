# FAQ Chatbot - RAG-Based Retrieval System

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline using semantic embeddings and vector search to deliver accurate answers to user questions based on a curated FAQ dataset.

## Overview

This application allows users to query a collection of FAQs scraped from an academic website and receive the most relevant answers. It uses `sentence-transformers` for embedding generation and `Weaviate Cloud` for vector similarity search. An alternate version using `FAISS` is also included for local vector store experimentation.

## Features

* Web scraping of questions, answers, tags, and suggested questions.
* Semantic embedding of FAQ data using `sentence-transformers`.
* Indexing and search powered by Weaviate Cloud (Hybrid Vector + Keyword search).
* Command-line and API-based interfaces.
* Docker/Render compatible backend architecture.

## Tech Stack

* **Language**: Python 3.10+
* **Embedding Model**: `sentence-transformers/all-mpnet-base-v2`
* **Vector DB**: Weaviate (via Cloud instance)
* **Web Scraping**: BeautifulSoup
* **Web Framework**: FastAPI
* **Hosting Options**: Render / Railway / Vercel Edge

## Folder Structure

```
├── app.py                  # FastAPI backend for FAQ querying
├── faq_data.json           # Scraped and cleaned FAQ dataset
├── scrape_faq.py           # Scraper to build faq_data.json
├── upload_to_weaviate.py   # Uploads embedded FAQ data to Weaviate
├── query_weaviate.py       # CLI script to perform hybrid query
├── faq_rag_demo.py         # FAISS-based local search fallback
├── requirements.txt        # Python dependencies
├── Procfile                # Render-compatible startup file
├── README.md               # Project documentation
```

## Usage

### 1. Scrape FAQ Data

```bash
python scrape_faq.py
```

### 2. Upload to Weaviate

Ensure you have your API key configured as an environment variable.

```bash
python upload_to_weaviate.py
```

### 3. Query CLI

```bash
python query_weaviate.py
```

### 4. Run Backend API

```bash
uvicorn app:app --reload
```

## Deployment

* Add your `Procfile` with: `web: uvicorn app:app --host=0.0.0.0 --port=${PORT:-8000}`
* Push to GitHub
* Deploy to [Render](https://render.com) or [Railway](https://railway.app)


## Author

CH24B050 - Summer AI Mini Project

