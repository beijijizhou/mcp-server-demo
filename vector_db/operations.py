# vector_db/operations.py
from typing import Union, List, Dict, Any
from .client import pinecone

def query_vectors(
    query: Union[str, List[float]],
    top_k: int = 5,
    filter: Dict[str, Any] = None,
    include_metadata: bool = True,
    include_values: bool = False
) -> Dict[str, Any]:
    """
    Query Pinecone with automatic connection handling
    
    Args:
        query: Text string or pre-computed embedding vector
        top_k: Number of results to return
        filter: Metadata filter dictionary
        include_metadata: Whether to include metadata in results
        include_values: Whether to include vector values in results
    """
    try:
        response = pinecone.get_index().query(
            namespace=pinecone.get_namespace(),
            query=query,
            top_k=top_k,
            filter=filter,
            include_metadata=include_metadata,
            include_values=include_values
        )
        
        return {
            "matches": [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata,
                    **({"values": match.values} if include_values else {})
                }
                for match in response.matches
            ]
        }
        
    except Exception as e:
        return {"error": str(e), "status": "failed"}

def upsert_vectors(vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Batch upsert vectors"""
    try:
        result = pinecone.get_index().upsert(
            namespace=pinecone.get_namespace(),
            vectors=vectors
        )
        return {"status": "success", "upserted_count": result.upserted_count}
    except Exception as e:
        return {"error": str(e), "status": "failed"}