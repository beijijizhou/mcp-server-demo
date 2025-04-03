
from vector_db.operations import query_vectors


results = query_vectors(
    query="promise",
    top_k=3,
    include_metadata=True
)

print("Query Results:")
for match in results.get("matches", []):
    print(f"\nID: {match['id']}")
    print(f"Score: {match['score']:.3f}")
    print("Metadata:")
    for k, v in match.get("metadata", {}).items():
        print(f"  {k}: {v}")