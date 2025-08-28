import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

# --- Step 1: Load and prepare data ---
def load_data(file_path):
    """Loads data from a JSON file with explicit UTF-8 encoding."""
    print(f"📄 Loading data from '{file_path}'...")
    try:
        # --- THIS IS THE FIX ---
        # We add encoding='utf-8' to tell Python how to read the file correctly.
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter out duplicates and format documents
        documents = []
        for entry in data:
            # This check assumes your JSON has an 'is_duplicate' field.
            # If not, you might want to remove the 'if' condition to include all items.
            if not entry.get('is_duplicate', False):
                text = f"Product: {entry.get('product', 'N/A')}\nPrice: {entry.get('price', 0)}\nSite: {entry.get('site', 'N/A')}"
                documents.append(text)
        
        print(f"✅ Loaded {len(documents)} unique documents.")
        return documents
    except FileNotFoundError:
        print(f"❌ ERROR: File not found at '{file_path}'. Please check the path.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: The file '{file_path}' is not a valid JSON file. Details: {e}")
        return None

# --- Step 2: Embed documents using a free, local model ---
def embed_documents(documents, model):
    """Encodes a list of text documents into numerical vectors."""
    print("🧠 Embedding documents...")
    embeddings = model.encode(documents)
    print("✅ Documents embedded successfully.")
    return np.array(embeddings)

# --- Step 3: Build FAISS index for fast similarity search ---
def build_index(embeddings):
    """Builds a FAISS index from a list of embeddings."""
    print("🏗️ Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print("✅ FAISS index built successfully.")
    return index

# --- Step 4: Retrieve top-k relevant documents for a query ---
def retrieve(query, model, index, documents, k=5):
    """Retrieves the most relevant documents for a given query."""
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)
    retrieved_docs = [documents[i] for i in indices[0] if i < len(documents)]
    return retrieved_docs

# --- Step 5: Generate an answer using the Gemini model ---
def generate_answer(query, retrieved_docs, gemini_api_key):
    """Generates a conversational answer based on the query and retrieved context."""
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    context = "\n\n---\n\n".join(retrieved_docs)
    prompt = f"""
    You are a helpful assistant. Answer the following question based ONLY on the context provided below.
    If the context doesn't contain the answer, simply say "I could not find relevant information in the dataset."

    CONTEXT:
    {context}
    
    QUESTION:
    {query}
    
    ANSWER:
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- Main function to run the RAG pipeline ---
def main():
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found. Please ensure it is set in your .env file.")

    # Load data from the specified path
    documents = load_data('C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/2_data_with_duplicates.json')
    if not documents:
        return # Stop if data loading failed

    # Load a free, powerful embedding model from SentenceTransformers
    print("\nDownloading/loading embedding model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Create the embeddings and the search index
    embeddings = embed_documents(documents, embedding_model)
    index = build_index(embeddings)
    
    # Start the interactive chat loop
    print("\n🤖 RAG Chat is ready! Ask questions about your prediction market data.")
    while True:
        query = input("\nEnter your question (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        # 1. Retrieve relevant documents
        retrieved_docs = retrieve(query, embedding_model, index, documents, k=5)
        
        # 2. Generate an answer using Gemini and the retrieved documents
        answer = generate_answer(query, retrieved_docs, GEMINI_API_KEY)
        
        print("\n🔍 Retrieved Documents:")
        for i, doc in enumerate(retrieved_docs):
            print(f"  {i+1}. {doc.replace('\n', ' | ')}")
        
        print("\n💡 Answer from Gemini:")
        print(answer)

if __name__ == "__main__":
    main()