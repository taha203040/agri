import chromadb
import uuid

client = chromadb.PersistentClient(path="./chroma_data")

collection = client.create_collection(name="agriculture")

with open("data.txt",'r',encoding="utf-8") as f :
    polices : list[str] =f.read().splitlines() 

collection.add(
    ids=[str(uuid.uuid4() ) for _ in polices],
    documents=polices,
    metadatas=[{"lines":line} for line in range(len(polices))]
)
# print(collection.peek())
results = collection.query(
    query_texts=[
        "what is the soile sampling guide for start planting "
    ],
    n_results=3
)
for i , qr in enumerate(results["documents"]):
    print(f"\nQuery{i}")
    print("\n".join(qr))