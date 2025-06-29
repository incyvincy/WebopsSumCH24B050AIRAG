import weaviate
from sentence_transformers import SentenceTransformer
import os

# Load the pre-trained sentence transformer model for semantic embeddings
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Initialize Weaviate client using environment variable or fallback URL
WEAVIATE_URL = os.getenv("WEAVIATE_URL") or "https://5pfynfulru2wsgokeozxnq.c0.asia-southeast1.gcp.weaviate.cloud"
API_KEY = os.getenv("my-webops-api-key-weaviate")

# Ensure API key is present; required for authentication with Weaviate cloud
if not API_KEY:
    raise RuntimeError("Missing required env var: my-webops-api-key-weaviate")

# Establish connection with the Weaviate cloud instance
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(API_KEY)
)

try:
    while True:
        # Prompt user for a question
        query = input("Ask a question (or 'exit'): ").strip()
        if query.lower() == "exit":
            break

        # Embed the input question using the transformer model
        embedding = model.encode(query).tolist()

        try:
            # Perform a hybrid query: combines keyword-based and vector-based search
            results = client.collections.get("FAQ").query.hybrid(
                query=query,
                vector=embedding,
                limit=3  # Limit results to top 3 matches
            )
        except weaviate.exceptions.WeaviateQueryError as e:
            # Handle query failures and provide user-friendly message
            print(f"\n[Query Error] {e}\nSuggestion: Make sure your ingested vectors used same embedding model.")
            continue

        # Display top results to the user
        for i, result in enumerate(results.objects):
            print(f"\n--- Result {i+1} ---")
            print(f"Q: {result.properties.get('question')}")
            print(f"A: {result.properties.get('answer')}")
            if result.properties.get("tag"):
                print(f"Tag: {result.properties.get('tag')}")
            if result.properties.get("link"):
                print(f"Link: {result.properties.get('link')}")
finally:
    # Close the client connection gracefully on exit
    client.close()
# Ensure the client connection is closed when done