# faq_api.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import weaviate
from sentence_transformers import SentenceTransformer
import os

app = FastAPI()

# Load model once
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Init Weaviate client
WEAVIATE_URL = os.getenv("WEAVIATE_URL") or "https://5pfynfulru2wsgokeozxnq.c0.asia-southeast1.gcp.weaviate.cloud"
API_KEY = os.getenv("my-webops-api-key-weaviate")

if not API_KEY:
    raise RuntimeError("Missing required env var: my-webops-api-key-weaviate")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(API_KEY)
)

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_faq(query: QueryRequest):
    q = query.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty query.")

    embedding = model.encode(q).tolist()
    try:
        results = client.collections.get("FAQ").query.hybrid(
            query=q,
            vector=embedding,
            limit=3
        )
    except weaviate.exceptions.WeaviateQueryError as e:
        raise HTTPException(status_code=500, detail=f"Weaviate error: {str(e)}")

    response = []
    for result in results.objects:
        response.append({
            "question": result.properties.get("question"),
            "answer": result.properties.get("answer"),
            "tag": result.properties.get("tag"),
            "link": result.properties.get("link"),
        })
    return {"results": response}
