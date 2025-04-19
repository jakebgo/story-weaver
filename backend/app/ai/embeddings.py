from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding service with a Sentence-BERT model.
        
        Args:
            model_name (str): Name of the Sentence-BERT model to use.
                            Default is "all-MiniLM-L6-v2" which is a good balance
                            of performance and quality.
        """
        self.model = SentenceTransformer(model_name)
        
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embeddings for a single text string.
        
        Args:
            text (str): The text to embed.
            
        Returns:
            np.ndarray: The embedding vector.
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts.
        
        Args:
            texts (List[str]): List of texts to embed.
            
        Returns:
            np.ndarray: Array of embedding vectors.
        """
        return self.model.encode(texts, convert_to_numpy=True)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors.
        
        Returns:
            int: The dimension of the embedding vectors.
        """
        return self.model.get_sentence_embedding_dimension() 