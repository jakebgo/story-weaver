import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from .vector_store import VectorStore
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class OutlineService:
    def __init__(self):
        """Initialize the outline service with Gemini 2.0 Flash."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            
            # Configure Gemini API
            genai.configure(api_key=api_key)
            
            # Initialize Gemini 2.0 Flash model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Initialize vector store and embedding service
            self.vector_store = VectorStore()
            self.embedding_service = EmbeddingService()
            
            logger.info("Successfully initialized OutlineService with Gemini 2.0 Flash")
        except Exception as e:
            logger.error(f"Failed to initialize OutlineService: {str(e)}")
            raise

    async def generate_outline(self, segment_ids: List[str], prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an outline based on the provided segment IDs.
        
        Args:
            segment_ids: List of segment IDs to use as context
            prompt: Optional prompt to guide the outline generation
            
        Returns:
            Dict containing the generated outline
        """
        try:
            # Retrieve segments from vector store
            segments = []
            for segment_id in segment_ids:
                segment = self.vector_store.get_segment_by_id(segment_id)
                if segment:
                    segments.append(segment["text"])
            
            if not segments:
                raise ValueError("No valid segments found")
            
            # Prepare the context
            context = "\n\n".join(segments)
            
            # Prepare the prompt
            if not prompt:
                prompt = """
                Based on the following transcript segments, generate a structured outline.
                The outline should:
                1. Have a clear title
                2. Be organized into main sections
                3. Include key points under each section
                4. Reference the source transcript segments using their IDs
                
                Format the outline as a JSON object with the following structure:
                {
                    "title": "Main title",
                    "sections": [
                        {
                            "heading": "Section heading",
                            "points": [
                                {
                                    "text": "Point description",
                                    "segment_ids": ["id1", "id2"]
                                }
                            ]
                        }
                    ]
                }
                """
            
            # Generate the outline
            response = self.model.generate_content(
                f"{prompt}\n\nTranscript segments:\n{context}"
            )
            
            # Parse the response
            try:
                import json
                outline = json.loads(response.text)
                logger.info("Successfully generated outline")
                return outline
            except json.JSONDecodeError:
                logger.error("Failed to parse Gemini response as JSON")
                return {
                    "error": "Failed to parse outline",
                    "raw_response": response.text
                }
                
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            raise

    async def analyze_transcript(self, segment_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze the transcript segments to identify topics, key moments, and key terms.
        
        Args:
            segment_ids: List of segment IDs to analyze
            
        Returns:
            Dict containing the analysis results
        """
        try:
            # Retrieve segments from vector store
            segments = []
            for segment_id in segment_ids:
                segment = self.vector_store.get_segment_by_id(segment_id)
                if segment:
                    segments.append(segment["text"])
            
            if not segments:
                raise ValueError("No valid segments found")
            
            # Prepare the context
            context = "\n\n".join(segments)
            
            # Prepare the analysis prompts
            topics_prompt = """
            Analyze the following transcript segments and identify the key topics and narrative beats.
            For each topic, provide:
            1. A clear title
            2. A brief description
            3. The segment IDs where this topic appears
            
            Format the response as a JSON object with the following structure:
            {
                "topics": [
                    {
                        "title": "Topic title",
                        "description": "Topic description",
                        "segment_ids": ["id1", "id2"]
                    }
                ]
            }
            """
            
            moments_prompt = """
            Identify the key moments, decisions, and questions in the following transcript segments.
            For each key moment, provide:
            1. A clear description of the moment
            2. The type (decision, question, revelation, etc.)
            3. The segment IDs where this moment appears
            
            Format the response as a JSON object with the following structure:
            {
                "key_moments": [
                    {
                        "description": "Description of the moment",
                        "type": "decision|question|revelation|etc",
                        "segment_ids": ["id1", "id2"]
                    }
                ]
            }
            """
            
            terms_prompt = """
            Extract the key terms and concepts from the following transcript segments.
            For each key term, provide:
            1. The term itself
            2. A brief definition or explanation
            3. The segment IDs where this term appears
            
            Format the response as a JSON object with the following structure:
            {
                "key_terms": [
                    {
                        "term": "The key term",
                        "definition": "Brief definition or explanation",
                        "segment_ids": ["id1", "id2"]
                    }
                ]
            }
            """
            
            # Generate the analyses
            topics_response = self.model.generate_content(
                f"{topics_prompt}\n\nTranscript segments:\n{context}"
            )
            
            moments_response = self.model.generate_content(
                f"{moments_prompt}\n\nTranscript segments:\n{context}"
            )
            
            terms_response = self.model.generate_content(
                f"{terms_prompt}\n\nTranscript segments:\n{context}"
            )
            
            # Parse the responses
            try:
                import json
                analysis = {
                    "topics": json.loads(topics_response.text),
                    "key_moments": json.loads(moments_response.text),
                    "key_terms": json.loads(terms_response.text)
                }
                logger.info("Successfully analyzed transcript")
                return analysis
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
                return {
                    "error": "Failed to parse analysis",
                    "raw_responses": {
                        "topics": topics_response.text,
                        "key_moments": moments_response.text,
                        "key_terms": terms_response.text
                    }
                }
                
        except Exception as e:
            logger.error(f"Error analyzing transcript: {str(e)}")
            raise

# Create a singleton instance
outline_service = OutlineService() 