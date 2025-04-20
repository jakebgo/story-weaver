import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        """Initialize the vector store with Qdrant client."""
        try:
            self.url = os.getenv("QDRANT_URL")
            self.api_key = os.getenv("QDRANT_API_KEY")
            
            if not self.url or not self.api_key:
                raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set")
            
            self.client = QdrantClient(url=self.url, api_key=self.api_key)
            self.collection_name = "story_segments"
            logger.info("Successfully initialized Qdrant client")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {str(e)}")
            raise

    def create_collection(self, vector_size: int) -> None:
        """
        Create a new collection if it doesn't exist.
        
        Args:
            vector_size: Dimension of the vectors to be stored
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(col.name == self.collection_name for col in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                logger.info(f"Created new collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise

    def upsert_segments(
        self,
        segment_ids: List[str],
        vectors: np.ndarray,
        texts: List[str],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Upsert segments into the vector store.
        
        Args:
            segment_ids: List of unique segment IDs
            vectors: numpy array of embeddings
            texts: List of text segments
            metadata: List of metadata dictionaries
        """
        try:
            points = []
            for i, (segment_id, vector, text, meta) in enumerate(zip(segment_ids, vectors, texts, metadata)):
                point = models.PointStruct(
                    id=segment_id,
                    vector=vector.tolist(),
                    payload={
                        "text": text,
                        **meta
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully upserted {len(points)} segments")
        except Exception as e:
            logger.error(f"Error upserting segments: {str(e)}")
            raise

    def search_similar(
        self,
        query_vector: np.ndarray,
        limit: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar segments.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of dictionaries containing search results
        """
        try:
            # Ensure the vector is flattened and converted to a list
            if len(query_vector.shape) > 1:
                query_vector = query_vector.flatten()
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=limit,
                score_threshold=score_threshold
            )
            
            return [
                {
                    "score": hit.score,
                    "text": hit.payload["text"],
                    **{k: v for k, v in hit.payload.items() if k != "text"}
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Error searching similar segments: {str(e)}")
            raise
            
    def get_segment_by_id(self, segment_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific segment by its ID.
        
        Args:
            segment_id: The ID of the segment to retrieve
            
        Returns:
            Dict containing the segment data or None if not found
        """
        try:
            # Use the scroll API to retrieve the segment by ID
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="id",
                            match=models.MatchValue(value=segment_id)
                        )
                    ]
                ),
                limit=1
            )
            
            # Check if we found the segment
            if results[0]:
                point = results[0][0]
                return {
                    "id": point.id,
                    "text": point.payload["text"],
                    **{k: v for k, v in point.payload.items() if k != "text"}
                }
            else:
                logger.warning(f"Segment with ID {segment_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error retrieving segment by ID: {str(e)}")
            raise
            
    def get_segments_by_ids(self, segment_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve multiple segments by their IDs.
        
        Args:
            segment_ids: List of segment IDs to retrieve
            
        Returns:
            List of dictionaries containing segment data
        """
        try:
            segments = []
            for segment_id in segment_ids:
                segment = self.get_segment_by_id(segment_id)
                if segment:
                    segments.append(segment)
            
            logger.info(f"Retrieved {len(segments)} segments by ID")
            return segments
        except Exception as e:
            logger.error(f"Error retrieving segments by IDs: {str(e)}")
            raise 