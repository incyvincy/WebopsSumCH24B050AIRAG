import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

FAQ_JSON = "faq_data.json"
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
TOP_K = 3

def load_faq_data(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_documents(faq_data):
    docs = []
    for item in faq_data:
        docs.append(
            Document(
                page_content=item["answer"],
                metadata={
                    "question": item["question"],
                    "tag": item.get("tag", "Unknown"),
                    "href": item.get("href", "")
                }
            )
        )
    return docs

def build_vectorstore(docs, embed_model):
    embeddings = HuggingFaceEmbeddings(model_name=embed_model)
    return FAISS.from_documents(docs, embeddings)

def rag_query(vectorstore, user_query, top_k=TOP_K):
    return vectorstore.similarity_search(user_query, k=top_k)

def print_results(results):
    print("\nTop Answers:")
    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Q: {doc.metadata['question']}")
        print(f"A: {doc.page_content}")
        print(f"Tag: {doc.metadata['tag']}")
        print(f"Link: {doc.metadata['href']}")

def main():
    print("Loading FAQ data and building vector store (this may take a few seconds)...")
    faq_data = load_faq_data(FAQ_JSON)
    docs = build_documents(faq_data)
    vectorstore = build_vectorstore(docs, EMBED_MODEL)
    print("Ready! Type your question (or 'exit' to quit):")
    while True:
        user_q = input("\nYour question: ").strip()
        if user_q.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        results = rag_query(vectorstore, user_q, top_k=TOP_K)
        print_results(results)

if __name__ == "__main__":
    main()