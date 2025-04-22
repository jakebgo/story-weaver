import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import json
from jsonschema import validate, ValidationError
import time

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

class GeminiService:
    def __init__(self):
        """Initialize the Gemini API service."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            
            # Configure the Gemini API
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            
            logger.info("Successfully initialized Gemini API service")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API service: {str(e)}")
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
    
    def generate_outline(self, context: List[str], prompt: str) -> Dict[str, Any]:
        """
        Generate an outline based on the provided context and prompt.
        
        Args:
            context: List of text segments from the transcript
            prompt: The prompt to guide the outline generation
            
        Returns:
            Dict containing the generated outline and metadata
        """
        try:
            # Format the context for the prompt
            formatted_context = "\n\n".join(context)
            logger.info(f"Generating outline for {len(context)} segments")
            
            # Create the full prompt
            full_prompt = f"""
            Based on the following transcript segments, generate a structured outline.
            
            Transcript segments:
            {formatted_context}
            
            {prompt}
            
            Format the outline as a JSON object with the following structure:
            {{
                "title": "Main title of the outline",
                "sections": [
                    {{
                        "heading": "Section heading",
                        "points": [
                            {{
                                "text": "Point description",
                                "segment_ids": ["id1", "id2"]  # IDs of relevant transcript segments
                            }}
                        ]
                    }}
                ]
            }}
            """
            
            # Generate the response with retries
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempt {attempt + 1} of {max_retries}")
                    
                    # Generate the response
                    response = self.model.generate_content(full_prompt)
                    logger.debug(f"Raw response: {response.text}")
                    
                    # Parse the response
                    outline = json.loads(response.text)
                    
                    # Validate the outline structure
                    if self._validate_outline(outline):
                        logger.info("Successfully generated and validated outline")
                        return outline
                    else:
                        logger.warning(f"Invalid outline structure on attempt {attempt + 1}")
                        if attempt == max_retries - 1:
                            raise ValueError("Failed to generate valid outline structure")
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse Gemini response as JSON on attempt {attempt + 1}: {str(e)}")
                    logger.debug(f"Raw response: {response.text}")
                    if attempt == max_retries - 1:
                        raise ValueError("Failed to parse outline")
                        
                except Exception as e:
                    logger.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                
                # Wait before retrying
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
        except Exception as e:
            logger.error(f"Error generating outline: {str(e)}")
            raise
    
    def analyze_topics(self, context: List[str]) -> Dict[str, Any]:
        """
        Analyze the transcript to identify key topics and narrative beats.
        
        Args:
            context: List of text segments from the transcript
            
        Returns:
            Dict containing identified topics and their relevance
        """
        try:
            # Format the context for the prompt
            formatted_context = "\n\n".join(context)
            logger.info(f"Analyzing topics for {len(context)} segments")
            
            # Create the prompt
            prompt = f"""
            Analyze the following transcript segments and identify the key topics and narrative beats.
            
            Transcript segments:
            {formatted_context}
            
            For each topic or beat, provide:
            1. A clear title
            2. A brief description
            3. The segment IDs where this topic appears
            
            Format the response as a JSON object with the following structure:
            {{
                "topics": [
                    {{
                        "title": "Topic title",
                        "description": "Topic description",
                        "segment_ids": ["id1", "id2"]
                    }}
                ]
            }}
            """
            
            # Generate the response with retries
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempt {attempt + 1} of {max_retries}")
                    
                    # Generate the response
                    response = self.model.generate_content(prompt)
                    logger.debug(f"Raw response: {response.text}")
                    
                    # Parse the response
                    topics = json.loads(response.text)
                    logger.info("Successfully analyzed topics")
                    return topics
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse Gemini response as JSON on attempt {attempt + 1}: {str(e)}")
                    logger.debug(f"Raw response: {response.text}")
                    if attempt == max_retries - 1:
                        return {
                            "error": "Failed to parse topics",
                            "raw_response": response.text
                        }
                        
                except Exception as e:
                    logger.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                
                # Wait before retrying
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
        except Exception as e:
            logger.error(f"Error analyzing topics: {str(e)}")
            raise
    
    def identify_key_moments(self, context: List[str]) -> Dict[str, Any]:
        """
        Identify key moments, decisions, and questions in the transcript.
        
        Args:
            context: List of text segments from the transcript
            
        Returns:
            Dict containing identified key moments
        """
        try:
            # Format the context for the prompt
            formatted_context = "\n\n".join(context)
            logger.info(f"Identifying key moments for {len(context)} segments")
            
            # Create the prompt
            prompt = f"""
            Identify the key moments, decisions, and questions in the following transcript segments.
            
            Transcript segments:
            {formatted_context}
            
            For each key moment, provide:
            1. A clear description of the moment
            2. The type (decision, question, revelation, etc.)
            3. The segment IDs where this moment appears
            
            Format the response as a JSON object with the following structure:
            {{
                "key_moments": [
                    {{
                        "description": "Description of the moment",
                        "type": "decision|question|revelation|etc",
                        "segment_ids": ["id1", "id2"]
                    }}
                ]
            }}
            """
            
            # Generate the response with retries
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempt {attempt + 1} of {max_retries}")
                    
                    # Generate the response
                    response = self.model.generate_content(prompt)
                    logger.debug(f"Raw response: {response.text}")
                    
                    # Parse the response
                    moments = json.loads(response.text)
                    logger.info("Successfully identified key moments")
                    return moments
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse Gemini response as JSON on attempt {attempt + 1}: {str(e)}")
                    logger.debug(f"Raw response: {response.text}")
                    if attempt == max_retries - 1:
                        return {
                            "error": "Failed to parse key moments",
                            "raw_response": response.text
                        }
                        
                except Exception as e:
                    logger.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                
                # Wait before retrying
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
        except Exception as e:
            logger.error(f"Error identifying key moments: {str(e)}")
            raise
    
    def extract_key_terms(self, context: List[str]) -> Dict[str, Any]:
        """
        Extract key terms and concepts from the transcript.
        
        Args:
            context: List of text segments from the transcript
            
        Returns:
            Dict containing extracted key terms
        """
        try:
            # Format the context for the prompt
            formatted_context = "\n\n".join(context)
            logger.info(f"Extracting key terms from {len(context)} segments")
            
            # Create the prompt
            prompt = f"""
            Extract the key terms, concepts, and important phrases from the following transcript segments.
            
            Transcript segments:
            {formatted_context}
            
            For each key term, provide:
            1. The term itself
            2. A brief definition or explanation
            3. The segment IDs where this term appears
            
            Format the response as a JSON object with the following structure:
            {{
                "key_terms": [
                    {{
                        "term": "The key term",
                        "definition": "Brief definition or explanation",
                        "segment_ids": ["id1", "id2"]
                    }}
                ]
            }}
            """
            
            # Generate the response with retries
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    logger.info(f"Attempt {attempt + 1} of {max_retries}")
                    
                    # Generate the response
                    response = self.model.generate_content(prompt)
                    logger.debug(f"Raw response: {response.text}")
                    
                    # Parse the response
                    terms = json.loads(response.text)
                    logger.info("Successfully extracted key terms")
                    return terms
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse Gemini response as JSON on attempt {attempt + 1}: {str(e)}")
                    logger.debug(f"Raw response: {response.text}")
                    if attempt == max_retries - 1:
                        return {
                            "error": "Failed to parse key terms",
                            "raw_response": response.text
                        }
                        
                except Exception as e:
                    logger.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                
                # Wait before retrying
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
        except Exception as e:
            logger.error(f"Error extracting key terms: {str(e)}")
            raise 