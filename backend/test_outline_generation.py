import os
import logging
import asyncio
from dotenv import load_dotenv
from app.services.outline_service import OutlineService
from app.services.vector_store import VectorStore
from app.services.embedding_service import EmbeddingService
import uuid
import pyttsx3
import wave
import numpy as np
from gtts import gTTS
import soundfile as sf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_audio(text, output_path="test_audio.wav", sample_rate=16000):
    """
    Create a WAV file with speech content using Google Text-to-Speech.
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save the WAV file
        sample_rate (int): Target sample rate for the audio file
    
    Returns:
        str: Path to the created audio file
    """
    try:
        # Create a temporary MP3 file
        temp_mp3 = "temp_speech.mp3"
        tts = gTTS(text=text, lang='en')
        tts.save(temp_mp3)
        
        # Read the audio file
        audio_data, current_sample_rate = sf.read(temp_mp3)
        
        # Resample if necessary
        if current_sample_rate != sample_rate:
            # Simple resampling using numpy
            duration = len(audio_data) / current_sample_rate
            new_length = int(duration * sample_rate)
            audio_data = np.interp(
                np.linspace(0, len(audio_data), new_length),
                np.arange(len(audio_data)),
                audio_data
            )
        
        # Save as WAV
        sf.write(output_path, audio_data, sample_rate)
        
        # Clean up temporary file
        os.remove(temp_mp3)
        
        logger.info(f"Created test audio file at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating test audio: {str(e)}")
        raise

# Test data - Harry Potter narrative segments
TEST_SEGMENTS = [
    {
        "text": "Harry Potter was a normal boy, or so he thought, until his eleventh birthday when he received a letter from Hogwarts School of Witchcraft and Wizardry.",
        "metadata": {
            "source": "test",
            "chapter": 1,
            "character": "Harry Potter"
        }
    },
    {
        "text": "The letter revealed that Harry was a wizard and had been accepted to Hogwarts. His life would never be the same again.",
        "metadata": {
            "source": "test",
            "chapter": 1,
            "character": "Harry Potter"
        }
    },
    {
        "text": "At Hogwarts, Harry made friends with Ron Weasley and Hermione Granger. Together, they would face many challenges and adventures.",
        "metadata": {
            "source": "test",
            "chapter": 1,
            "character": ["Harry Potter", "Ron Weasley", "Hermione Granger"]
        }
    }
]

async def test_outline_generation():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize services
        outline_service = OutlineService()
        vector_store = VectorStore()
        embedding_service = EmbeddingService()
        
        # Generate test audio with speech content
        test_text = " ".join(segment["text"] for segment in TEST_SEGMENTS)
        audio_path = create_test_audio(test_text)
        
        # Generate embeddings and upsert segments
        segment_ids = []
        for segment in TEST_SEGMENTS:
            # Generate unique ID for segment
            segment_id = str(uuid.uuid4())
            segment_ids.append(segment_id)
            
            # Generate embedding
            embedding = embedding_service.embed_texts([segment["text"]])[0]
            
            # Upsert to vector store
            vector_store.upsert_segments(
                segment_ids=[segment_id],
                vectors=embedding.reshape(1, -1),  # Reshape to 2D array
                texts=[segment["text"]],
                metadata=[segment["metadata"]]
            )
            
            logger.info(f"Successfully upserted segment {segment_id}")
        
        # Test outline generation with custom prompt
        custom_prompt = """
        Create a detailed outline of the story focusing on:
        1. Character introductions
        2. Key plot points
        3. Important relationships
        
        Make sure to reference the source segments using their IDs.
        """
        
        logger.info("Generating outline...")
        outline = await outline_service.generate_outline(segment_ids, custom_prompt)
        
        # Log the results
        logger.info("Generated outline:")
        logger.info(f"Title: {outline['title']}")
        for section in outline['sections']:
            logger.info(f"\nSection: {section['heading']}")
            for point in section['points']:
                logger.info(f"- {point['text']}")
                logger.info(f"  Source segments: {point['segment_ids']}")
        
        # Test with invalid segment IDs
        logger.info("\nTesting with invalid segment IDs...")
        invalid_ids = ["invalid_id_1", "invalid_id_2"]
        try:
            await outline_service.generate_outline(invalid_ids)
        except ValueError as e:
            logger.info(f"Expected error caught: {str(e)}")
        
        logger.info("Outline generation test completed successfully")
        
    except Exception as e:
        logger.error(f"Error during outline generation test: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_outline_generation()) 