# Import required libraries
from fastapi import FastAPI, HTTPException  # FastAPI for API routes, HTTPException for handling errors
from pydantic import BaseModel  # Used to define request body structure and validation
from sentence_transformers import SentenceTransformer  # For turning text into vector embeddings
import weaviate  # Weaviate client to connect and query vector database
import os  # For reading environment variables like API keys

# Create a FastAPI instance
app = FastAPI()

# Define what kind of input data the /ask endpoint will accept
class QueryInput(BaseModel):
    question: str  # User will send a "question" as a string

# Load the sentence embedding model (used to convert question to vector)
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

# Set Weaviate cloud URL from environment or use default value
WEAVIATE_URL = os.getenv("WEAVIATE_URL")

# Get the API key from environment variable
API_KEY = os.getenv("my-webops-api-key-weaviate")

# If no API key is found, raise an error and stop the app
if not API_KEY:
    raise RuntimeError("Missing env var: my-webops-api-key-weaviate")

# Connect to Weaviate cloud instance using URL and API key
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(API_KEY)
)

# Define the POST endpoint that receives a question and returns similar answers
@app.post("/ask", response_model=dict)
def ask_faq(input_data: QueryInput):
    query = input_data.question.strip()  # Remove extra spaces from the input question
    if not query:
        raise HTTPException(status_code=422, detail="Empty query")  # If question is empty, return error

    embedding = model.encode(query).tolist()  # Convert question to vector format

    try:
        # Perform hybrid search on Weaviate using both text and vector
        results = client.collections.get("FAQ").query.hybrid(
            query=query,
            vector=embedding,
            limit=3  # Limit to top 3 results
        )
    except weaviate.exceptions.WeaviateQueryError as e:
        raise HTTPException(status_code=500, detail=str(e))  # If search fails, return server error

    if not results.objects:
        return {"answer": "No matching answers found."}  # No results case

    answers = []
    for result in results.objects:
        # Extract and return relevant fields from each matched object
        answers.append({
            "question": result.properties.get("question"),
            "answer": result.properties.get("answer"),
            "tag": result.properties.get("tag"),
            "link": result.properties.get("link")
        })

    return {"results": answers}  # Final list of results sent back to the user