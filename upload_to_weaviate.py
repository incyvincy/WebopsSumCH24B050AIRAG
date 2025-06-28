import weaviate
from sentence_transformers import SentenceTransformer
import json
import sys
import os
from weaviate.collections.classes.config import DataType  # ✅ Compatible import path for Weaviate v4.15+

WEAVIATE_URL = "https://5pfynfulru2wsgokeozxnq.c0.asia-southeast1.gcp.weaviate.cloud"
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
FAQ_JSON = "faq_data.json"
CLASS_NAME = "FAQ"

API_KEY = os.environ.get("my-webops-api-key-weaviate")
if not API_KEY:
    raise RuntimeError("Environment variable 'my-webops-api-key-weaviate' not set!")

try:
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL,
        auth_credentials=weaviate.auth.AuthApiKey(API_KEY)
    )
except Exception as e:
    print(f"Failed to connect to Weaviate: {e}")
    sys.exit(1)

# Create schema if not exists
try:
    if not client.collections.exists(CLASS_NAME):
        client.collections.create(
            name=CLASS_NAME,
            properties=[
                {"name": "question", "data_type": DataType.TEXT},
                {"name": "answer", "data_type": DataType.TEXT},
                {"name": "tag", "data_type": DataType.TEXT},
                {"name": "href", "data_type": DataType.TEXT},
            ]
        )
except Exception as e:
    print(f"Schema creation error: {e}")
    client.close()
    sys.exit(1)

# Load FAQ data
try:
    with open(FAQ_JSON, "r", encoding="utf-8") as f:
        faq_data = json.load(f)
except Exception as e:
    print(f"Error loading FAQ JSON: {e}")
    client.close()
    sys.exit(1)

# Load embedding model
try:
    model = SentenceTransformer(EMBED_MODEL)
except Exception as e:
    print(f"Error loading embedding model: {e}")
    client.close()
    sys.exit(1)

success, fail = 0, 0
for item in faq_data:
    try:
        vector = model.encode(item["question"]).tolist()
        data_obj = {
            "question": item["question"],
            "answer": item["answer"],
            "tag": item.get("tag", "Unknown"),
            "href": item.get("href", ""),
        }
        client.collections.get(CLASS_NAME).data.insert(
            properties=data_obj,
            vector=vector
        )
        success += 1
    except Exception as e:
        print(f"Failed to upload: {item.get('question', 'Unknown Question')} | Error: {e}")
        fail += 1

print(f"Upload complete! Success: {success}, Fail: {fail}")
if fail > 0:
    print("Some items failed to upload. Check the logs for details.")

client.close()
