import os
import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        """Initialize the embedding service with the SentenceTransformer model."""
        try:
            # Use a lightweight but effective model for embeddings
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Successfully initialized embedding model")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            raise

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings produced by the model."""
        return self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for one or more texts.
        
        Args:
            texts: A single text string or list of text strings
            
        Returns:
            numpy array of embeddings with shape (n_texts, embedding_dim)
        """
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            logger.debug(f"Generated embeddings with shape: {embeddings.shape}")
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise 