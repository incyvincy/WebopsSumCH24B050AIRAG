import weaviate
from sentence_transformers import SentenceTransformer
import os

#eLoad sentence transformer model
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

#Init Weaviate client (fixed deprecated & missing env handling)
WEAVIATE_URL = os.getenv("WEAVIATE_URL") or "https://5pfynfulru2wsgokeozxnq.c0.asia-southeast1.gcp.weaviate.cloud"
API_KEY = os.getenv("my-webops-api-key-weaviate")

if not API_KEY:
    raise RuntimeError("Missing required env var: my-webops-api-key-weaviate")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(API_KEY)
)

try:
    while True:
        query = input("Ask a question (or 'exit'): ").strip()
        if query.lower() == "exit":
            break

        #Embed input
        embedding = model.encode(query).tolist()

        try:
            # Performing hybrid search (semantic + keyword based)
            results = client.collections.get("FAQ").query.hybrid(
                query=query,
                vector=embedding,
                limit=3
            )
        except weaviate.exceptions.WeaviateQueryError as e:
            print(f"\n[Query Error] {e}\nSuggestion: Make sure your ingested vectors used same embedding model.")
            continue

        for i, result in enumerate(results.objects):
            print(f"\n--- Result {i+1} ---")
            print(f"Q: {result.properties.get('question')}")
            print(f"A: {result.properties.get('answer')}")
            if result.properties.get("tag"):
                print(f"Tag: {result.properties.get('tag')}")
            if result.properties.get("link"):
                print(f"Link: {result.properties.get('link')}")
finally:
    client.close()