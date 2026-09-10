import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Initialize splitter ONCE, reuse for every document
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "]
)

def load_and_chunk(raw_dir: str, source_name: str, country: str, category: str):
    all_chunks = []
    if not os.path.exists(raw_dir):
        return all_chunks
    for filename in os.listdir(raw_dir):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(raw_dir, filename)
        
        # Load the raw text file into memory
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        
        # This is the actual "loading into the splitter" step
        chunks = splitter.split_text(text)
        
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{source_name}_{filename}_{i}",
                "text": chunk,
                "metadata": {
                    "source": source_name,
                    "country": country,
                    "category": category,
                    "refresh_type": "weekly",
                    "date_collected": "2026-09-03"
                }
            })
    return all_chunks

# Ensure output directory exists
os.makedirs("data/processed", exist_ok=True)

# Run per source/country
germany_chunks = load_and_chunk("data/raw/germany", "germany_sources", "Germany", "living_and_visa")
canada_chunks = load_and_chunk("data/raw/canada", "canada_sources", "Canada", "living_and_visa")
australia_chunks = load_and_chunk("data/raw/australia", "australia_sources", "Australia", "living_and_visa")
usa_chunks = load_and_chunk("data/raw/usa", "usa_sources", "USA", "living_and_visa")

# Save chunked output BEFORE embedding — this is your checkpoint
all_chunks = germany_chunks + canada_chunks + australia_chunks + usa_chunks
with open("data/processed/chunks.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2)

print(f"Total chunks created: {len(all_chunks)}")