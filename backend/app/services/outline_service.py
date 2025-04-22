import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from .vector_store import VectorStore
from .embedding_service import EmbeddingService
import json
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)

# Define JSON schemas for validation
OUTLINE_SCHEMA = {
    "type": "object",
    "required": ["title", "sections"],
    "properties": {
        "title": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["heading", "points"],
                "properties": {
                    "heading": {"type": "string"},
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["text", "segment_ids"],
                            "properties": {
                                "text": {"type": "string"},
                                "segment_ids": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

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

    def _validate_segment_ids(self, segment_ids: List[str]) -> List[str]:
        """
        Validate that the provided segment IDs exist in the vector store.
        
        Args:
            segment_ids: List of segment IDs to validate
            
        Returns:
            List of valid segment IDs
        """
        try:
            logger.info(f"Validating {len(segment_ids)} segment IDs")
            logger.debug(f"Segment IDs to validate: {segment_ids}")
            
            valid_ids = []
            invalid_ids = []
            
            for segment_id in segment_ids:
                segment = self.vector_store.get_segment_by_id(segment_id)
                if segment:
                    valid_ids.append(segment_id)
                    logger.debug(f"Segment {segment_id} is valid")
                else:
                    invalid_ids.append(segment_id)
                    logger.warning(f"Segment {segment_id} not found in vector store")
            
            logger.info(f"Validation complete: {len(valid_ids)} valid, {len(invalid_ids)} invalid")
            if invalid_ids:
                logger.warning(f"Invalid segment IDs: {invalid_ids}")
            
            return valid_ids
        except Exception as e:
            logger.error(f"Error validating segment IDs: {str(e)}")
            raise

    def _validate_outline(self, outline: Dict[str, Any]) -> bool:
        """
        Validate the outline structure against the schema.
        
        Args:
            outline: The outline to validate
            
        Returns:
            bool indicating if the outline is valid
        """
        try:
            validate(instance=outline, schema=OUTLINE_SCHEMA)
            return True
        except ValidationError as e:
            logger.error(f"Outline validation failed: {str(e)}")
            return False

    async def generate_outline(self, segment_ids: List[str], prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an outline from the provided segment IDs using RAG.
        
        Args:
            segment_ids: List of segment IDs to include in the outline
            prompt: Optional prompt to guide the outline generation
            
        Returns:
            Generated outline as a dictionary
        """
        try:
            logger.info(f"Generating outline for {len(segment_ids)} segments")
            logger.debug(f"Segment IDs: {segment_ids}")
            
            # Validate segment IDs
            valid_ids = self._validate_segment_ids(segment_ids)
            if not valid_ids:
                logger.error("No valid segment IDs found")
                raise ValueError("No valid segment IDs provided")
            
            logger.info(f"Using {len(valid_ids)} valid segment IDs for outline generation")
            
            # Get segments from vector store
            segments = self.vector_store.get_segments_by_ids(valid_ids)
            if not segments:
                logger.error("No segments found for valid IDs")
                raise ValueError("No segments found for valid IDs")
            
            logger.info(f"Retrieved {len(segments)} segments from vector store")
            
            # Prepare the context by combining segments with their IDs
            context = "\n\n".join([
                f"[Segment {seg['id']}]: {seg['text']}"
                for seg in segments
            ])
            
            # Prepare the outline generation prompt
            outline_prompt = prompt or """
            Create a structured story outline from the following transcript segments.
            The outline should:
            1. Have a clear title that captures the main theme
            2. Be organized into logical sections
            3. Include key points under each section
            4. Reference the source segment IDs for each point
            
            Format the response as a JSON object with the following structure:
            {
                "title": "Main title of the outline",
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
            
            Ensure that:
            1. Each point references at least one segment ID
            2. The structure is hierarchical and logical
            3. The content is clear and concise
            4. The outline captures the main narrative flow
            """
            
            # Generate outline using Gemini with the enhanced prompt
            response = self.model.generate_content(
                f"""
                Based on the following transcript segments, generate a structured outline.
                
                Transcript segments:
                {context}
                
                {outline_prompt}
                
                IMPORTANT: Your response must be a valid JSON object with the following structure:
                {{
                    "title": "Main title of the outline",
                    "sections": [
                        {{
                            "heading": "Section heading",
                            "points": [
                                {{
                                    "text": "Point description",
                                    "segment_ids": ["id1", "id2"]
                                }}
                            ]
                        }}
                    ]
                }}
                
                Do not include any text before or after the JSON object.
                """
            )
            
            if not response or not response.text:
                logger.error("Failed to generate outline from Gemini service")
                raise ValueError("Failed to generate outline")
            
            # Parse and validate the outline
            try:
                # Clean up the response text to ensure it's valid JSON
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                outline = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
                logger.error(f"Raw response: {response.text}")
                raise ValueError("Invalid outline format")
            
            # Validate outline structure
            if not self._validate_outline(outline):
                logger.error("Generated outline failed validation")
                raise ValueError("Invalid outline structure")
            
            logger.info("Successfully generated and validated outline")
            return outline
            
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