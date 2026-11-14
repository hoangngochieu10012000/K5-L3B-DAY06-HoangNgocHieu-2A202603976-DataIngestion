import os
import sys
import uuid
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

db_path = Path("starter/results/test_qdrant_db")
client = QdrantClient(path=str(db_path))

collection_name = "test_collection"
if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=4, distance=Distance.COSINE)
)

# Test upsert
points = [
    PointStruct(
        id=str(uuid.uuid5(uuid.NAMESPACE_DNS, "c1")),
        vector=[0.1, 0.2, 0.3, 0.4],
        payload={"chunk_id": "c1", "page": 1, "section": "intro", "text": "Hello intro"}
    ),
    PointStruct(
        id=str(uuid.uuid5(uuid.NAMESPACE_DNS, "c2")),
        vector=[0.1, 0.2, 0.3, 0.5],
        payload={"chunk_id": "c2", "page": 2, "section": "theory", "text": "Hello theory"}
    )
]

client.upsert(collection_name=collection_name, points=points)
print("Upserted points:", client.count(collection_name).count)

# Re-upsert same points to test idempotence (no duplicates)
client.upsert(collection_name=collection_name, points=points)
print("Points after re-upsert (must still be 2):", client.count(collection_name).count)

# Test search without filter
res_no_filter = client.query_points(
    collection_name=collection_name,
    query=[0.1, 0.2, 0.3, 0.5],
    limit=2
).points
print("Search without filter:")
for r in res_no_filter:
    print(f"  id={r.payload['chunk_id']}, score={r.score:.4f}, section={r.payload['section']}")

# Test search with filter section == 'intro'
filt = Filter(must=[FieldCondition(key="section", match=MatchValue(value="intro"))])
res_filtered = client.query_points(
    collection_name=collection_name,
    query=[0.1, 0.2, 0.3, 0.5],
    query_filter=filt,
    limit=2
).points
print("Search with filter section=intro:")
for r in res_filtered:
    print(f"  id={r.payload['chunk_id']}, score={r.score:.4f}, section={r.payload['section']}")

client.close()
print("Qdrant local test passed successfully!")
