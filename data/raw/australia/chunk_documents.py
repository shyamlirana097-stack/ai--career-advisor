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
    for filename in os.listdir(raw_dir):
        filepath = os.path.join(raw_dir, filename)
        
        # Load the raw text file into memory
        with open(filepath, "r", encoding="utf-8") as f:
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

# Run per source
daad_chunks = load_and_chunk("data/raw/daad", "daad", "Germany", "visa_policy")
ircc_chunks = load_and_chunk("data/raw/ircc", "ircc", "Canada", "visa_policy")

# Save chunked output BEFORE embedding — this is your checkpoint
all_chunks = daad_chunks + ircc_chunks
with open("data/processed/chunks.json", "w") as f:
    json.dump(all_chunks, f, indent=2)

print(f"Total chunks created: {len(all_chunks)}")