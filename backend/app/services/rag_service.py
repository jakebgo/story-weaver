import logging
from typing import List, Dict, Any, Optional
from app.services.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService
from app.ai.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        """Initialize the RAG service with vector store and Gemini API."""
        try:
            self.vector_store = VectorStore()
            self.embedding_service = EmbeddingService()
            self.gemini_service = GeminiService()
            logger.info("Successfully initialized RAG service")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            raise
    
    def retrieve_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from the vector store based on a query.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of relevant text segments with their metadata
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.embed_texts(query)
            
            # Search the vector store
            results = self.vector_store.search_similar(
                query_vector=query_embedding,
                limit=limit
            )
            
            logger.info(f"Retrieved {len(results)} relevant segments")
            return results
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            raise
    
    def generate_outline(self, segment_ids: List[str], prompt: str = None) -> Dict[str, Any]:
        """
        Generate an outline based on the provided segment IDs.
        
        Args:
            segment_ids: List of segment IDs to use as context
            prompt: Optional prompt to guide the outline generation
            
        Returns:
            Dict containing the generated outline
        """
        try:
            # Retrieve the text segments from the vector store
            segments_data = self.vector_store.get_segments_by_ids(segment_ids)
            segments = [segment["text"] for segment in segments_data]
            
            # Use default prompt if none provided
            if not prompt:
                prompt = "Generate a structured outline that captures the main points and flow of the discussion."
            
            # Generate the outline using Gemini
            outline = self.gemini_service.generate_outline(segments, prompt)
            
            logger.info("Successfully generated outline")
            return outline
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            raise
    
    def analyze_transcript(self, segment_ids: List[str]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of the transcript.
        
        Args:
            segment_ids: List of segment IDs to analyze
            
        Returns:
            Dict containing the analysis results
        """
        try:
            # Retrieve the text segments from the vector store
            segments_data = self.vector_store.get_segments_by_ids(segment_ids)
            segments = [segment["text"] for segment in segments_data]
            
            # Perform different types of analysis
            topics = self.gemini_service.analyze_topics(segments)
            key_moments = self.gemini_service.identify_key_moments(segments)
            key_terms = self.gemini_service.extract_key_terms(segments)
            
            # Combine the results
            analysis = {
                "topics": topics,
                "key_moments": key_moments,
                "key_terms": key_terms
            }
            
            logger.info("Successfully analyzed transcript")
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing transcript: {str(e)}")
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
            return self.vector_store.get_segment_by_id(segment_id)
        except Exception as e:
            logger.error(f"Error retrieving segment by ID: {str(e)}")
            raise 