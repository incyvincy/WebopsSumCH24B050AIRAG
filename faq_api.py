# faq_api.py
from fastapi import FastAPI, HTTPException, Request  # FastAPI core and error handling
from pydantic import BaseModel  # For input data validation
import weaviate  # For connecting to the Weaviate vector DB
from sentence_transformers import SentenceTransformer  # To convert text into embeddings
import os  # For environment variable access

app = FastAPI()

# Load the sentence embedding model (runs once)
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Setup Weaviate connection details
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
API_KEY = os.getenv("my-webops-api-key-weaviate")

# Ensure API key is available
if not API_KEY:
    raise RuntimeError("Missing required env var: my-webops-api-key-weaviate")

# Connect to Weaviate cloud instance
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(API_KEY)
)

# Define input format for the /ask endpoint
class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_faq(query: QueryRequest):
    q = query.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Empty query.")  # Handle empty input

    # Convert input question to embedding
    embedding = model.encode(q).tolist()

    try:
        # Perform hybrid search in Weaviate
        results = client.collections.get("FAQ").query.hybrid(
            query=q,
            vector=embedding,
            limit=3
        )
    except weaviate.exceptions.WeaviateQueryError as e:
        raise HTTPException(status_code=500, detail=f"Weaviate error: {str(e)}")

    # Build structured response
    response = []
    for result in results.objects:
        response.append({
            "question": result.properties.get("question"),
            "answer": result.properties.get("answer"),
            "tag": result.properties.get("tag"),
            "link": result.properties.get("link"),
        })
    return {"results": response}
