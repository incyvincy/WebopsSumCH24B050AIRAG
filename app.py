from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import weaviate
import os

app = FastAPI()

class QueryInput(BaseModel):
    question: str

model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

WEAVIATE_URL = os.getenv("WEAVIATE_URL") or "https://5pfynfulru2wsgokeozxnq.c0.asia-southeast1.gcp.weaviate.cloud"
API_KEY = os.getenv("my-webops-api-key-weaviate")

if not API_KEY:
    raise RuntimeError("Missing env var: my-webops-api-key-weaviate")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(API_KEY)
)

@app.post("/ask", response_model=dict)
def ask_faq(input_data: QueryInput):
    query = input_data.question.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Empty query")

    embedding = model.encode(query).tolist()

    try:
        results = client.collections.get("FAQ").query.hybrid(
            query=query,
            vector=embedding,
            limit=3
        )
    except weaviate.exceptions.WeaviateQueryError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not results.objects:
        return {"answer": "No matching answers found."}

    answers = []
    for result in results.objects:
        answers.append({
            "question": result.properties.get("question"),
            "answer": result.properties.get("answer"),
            "tag": result.properties.get("tag"),
            "link": result.properties.get("link")
        })

    return {"results": answers}
