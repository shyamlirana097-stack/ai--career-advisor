import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("career_roadmap_data")

results = collection.query(
    query_texts=["minimum bank balance required for student visa"],
    n_results=3,
    where={"country": "Germany"}
)

for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(meta["source"], "-", doc[:150], "...\n")