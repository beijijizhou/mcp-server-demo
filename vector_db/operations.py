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
        index = pinecone.get_index()
       
        response = index.search(namespace="js-rag",    query={
            "inputs": {"text": query},
            "top_k": 2
        })
       
        return response

    except Exception as e:
        return {"error": str(e), "status": "failed"}
