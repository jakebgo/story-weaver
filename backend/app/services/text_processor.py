import logging
from typing import List, Dict, Any
import uuid
from llama_index.core.node_parser import SentenceSplitter
from .embedding_service import EmbeddingService
from .vector_store import VectorStore
import nltk
from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        """Initialize the text processor with required services."""
        try:
            self.embedding_service = EmbeddingService()
            self.vector_store = VectorStore()
            self.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
            
            # Initialize vector store with correct dimension
            vector_size = self.embedding_service.get_embedding_dimension()
            self.vector_store.create_collection(vector_size)
            
            # Download required NLTK data
            nltk.download('punkt_tab', quiet=True)
            
            logger.info("Successfully initialized TextProcessor")
        except Exception as e:
            logger.error(f"Failed to initialize TextProcessor: {str(e)}")
            raise

    def process_transcript(self, transcript: str, metadata: Dict[str, Any]) -> List[str]:
        """
        Process a transcript by chunking it and storing in the vector database.
        
        Args:
            transcript: The transcript text to process
            metadata: Additional metadata to store with each chunk
            
        Returns:
            List of segment IDs for the stored chunks
        """
        try:
            # Split text into chunks
            chunks = self.node_parser.split_text(transcript)
            logger.debug(f"Split transcript into {len(chunks)} chunks")
            
            # Generate embeddings
            embeddings = self.embedding_service.embed_texts(chunks)
            
            # Generate unique IDs for each chunk
            segment_ids = [str(uuid.uuid4()) for _ in chunks]
            
            # Prepare metadata for each chunk
            chunk_metadata = [
                {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            # Store in vector database
            self.vector_store.upsert_segments(
                segment_ids=segment_ids,
                vectors=embeddings,
                texts=chunks,
                metadata=chunk_metadata
            )
            
            logger.info(f"Successfully processed transcript with {len(chunks)} chunks")
            return segment_ids
        except Exception as e:
            logger.error(f"Error processing transcript: {str(e)}")
            raise

    def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar text segments.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of similar segments with their metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_texts(query)
            
            # Search vector store
            results = self.vector_store.search_similar(
                query_vector=query_embedding,
                limit=limit
            )
            
            return results
        except Exception as e:
            logger.error(f"Error searching similar segments: {str(e)}")
            raise

    def process_text(self, text: str, min_length: int = 20) -> list[str]:
        """
        Process text into segments suitable for vector storage.
        
        Args:
            text: The text to process
            min_length: Minimum length of a segment in characters
            
        Returns:
            list[str]: List of text segments
        """
        try:
            # Split text into sentences
            sentences = sent_tokenize(text)
            
            # Process sentences into segments
            segments = []
            current_segment = ""
            
            for sentence in sentences:
                # If current segment is empty, start with this sentence
                if not current_segment:
                    current_segment = sentence
                # If adding this sentence would make segment too long, save current and start new
                elif len(current_segment) + len(sentence) > 512:  # Max token length for embedding
                    if len(current_segment) >= min_length:
                        segments.append(current_segment)
                    current_segment = sentence
                # Otherwise, add sentence to current segment
                else:
                    current_segment += " " + sentence
            
            # Add the last segment if it meets minimum length
            if current_segment and len(current_segment) >= min_length:
                segments.append(current_segment)
            
            return segments
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}", exc_info=True)
            raise 