# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import weaviate
import os

# Define request body
class QueryInput(BaseModel):
    question: str

# Load model
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Init Weaviate client
WEAVIATE_URL = os.getenv("WEAVIATE_URL") or "https://5pfynfulru2wsgokeozxnq.c0.asia-southeast1.gcp.weaviate.cloud"
API_KEY = os.getenv("my-webops-api-key-weaviate")

if not API_KEY:
    raise RuntimeError("Missing env var: my-webops-api-key-weaviate")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(API_KEY)
)

app = FastAPI()

@app.post("/ask")
def ask_faq(input: QueryInput):
    question = input.question.strip()
    embedding = model.encode(question).tolist()

    try:
        results = client.collections.get("FAQ").query.hybrid(
            query=question,
            vector=embedding,
            limit=3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid query failed: {str(e)}")

    response = []
    for result in results.objects:
        item = {
            "question": result.properties.get("question"),
            "answer": result.properties.get("answer"),
            "tag": result.properties.get("tag"),
            "link": result.properties.get("link"),
            "suggested_questions": result.properties.get("suggested_questions", [])
        }
        response.append(item)
    
    return {"results": response}
