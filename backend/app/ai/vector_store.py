from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from typing import List, Dict, Any, Optional
import numpy as np
import os
from datetime import datetime

class VectorStore:
    def __init__(self, collection_name: str = "transcript_segments"):
        """Initialize the vector store with Qdrant client.
        
        Args:
            collection_name (str): Name of the collection to use for storing vectors.
        """
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
    def create_collection(self, vector_size: int):
        """Create a new collection in Qdrant.
        
        Args:
            vector_size (int): The size of the vectors to be stored.
        """
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        
    def upsert_segments(
        self,
        segment_ids: List[str],
        vectors: np.ndarray,
        texts: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ):
        """Upsert transcript segments with their embeddings and metadata.
        
        Args:
            segment_ids (List[str]): List of unique segment IDs.
            vectors (np.ndarray): Array of embedding vectors.
            texts (List[str]): List of segment texts.
            metadata (Optional[List[Dict[str, Any]]]): List of metadata dictionaries.
        """
        if metadata is None:
            metadata = [{} for _ in segment_ids]
            
        # Add timestamp to metadata
        for meta in metadata:
            meta["timestamp"] = datetime.utcnow().isoformat()
            
        points = [
            models.PointStruct(
                id=segment_id,
                vector=vector.tolist(),
                payload={
                    "text": text,
                    **meta
                }
            )
            for segment_id, vector, text, meta in zip(segment_ids, vectors, texts, metadata)
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
    def search_similar(
        self,
        query_vector: np.ndarray,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar segments using a query vector.
        
        Args:
            query_vector (np.ndarray): The query embedding vector.
            limit (int): Maximum number of results to return.
            score_threshold (float): Minimum similarity score threshold.
            
        Returns:
            List[Dict[str, Any]]: List of search results with scores and payloads.
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit,
            score_threshold=score_threshold
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload["text"],
                **{k: v for k, v in hit.payload.items() if k != "text"}
            }
            for hit in results
        ] 