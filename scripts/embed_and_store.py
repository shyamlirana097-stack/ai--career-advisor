import os
import json
import chromadb

# Suppress Windows HuggingFace symlink cache warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from sentence_transformers import SentenceTransformer

# Step A: Load your chunked data from the checkpoint file
with open("data/processed/chunks.json", "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

print(f"Loaded {len(all_chunks)} chunks")

# Step B: Load the embedding model with local cache
cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=cache_dir)

# Step C: Extract just the text for embedding (metadata stays separate for now)
texts = [chunk["text"] for chunk in all_chunks]

# Step D: Generate embeddings — this is the actual "embedding" step
embeddings = model.encode(texts, show_progress_bar=True)

# Step E: Set up ChromaDB persistent storage
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("career_roadmap_data")

# Step F: Push everything into ChromaDB — text + vector + metadata + id, together
collection.add(
    ids=[chunk["id"] for chunk in all_chunks],
    documents=texts,
    embeddings=embeddings.tolist(),
    metadatas=[chunk["metadata"] for chunk in all_chunks]
)

print(f"Stored {collection.count()} chunks in ChromaDB")
