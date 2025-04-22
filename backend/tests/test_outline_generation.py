import asyncio
import wave
import numpy as np
import os
from app.services.outline_service import OutlineService
from app.services.transcription_service import TranscriptionService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.text_processor import TextProcessor

async def test_outline_generation():
    """Test the complete outline generation pipeline."""
    try:
        # Initialize services
        outline_service = OutlineService()
        transcription_service = TranscriptionService()
        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        text_processor = TextProcessor()
        
        # Create a test audio file with speech-like content
        sample_rate = 16000  # Standard sample rate for speech
        duration = 5  # 5 seconds of audio
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Generate a simple sine wave that mimics speech frequencies
        frequency = 440  # A4 note
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Normalize and convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Save as WAV file
        test_audio_path = "test_audio.wav"
        with wave.open(test_audio_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        print("✅ Created test audio file")

        # Read and transcribe the audio file
        with open(test_audio_path, 'rb') as audio_file:
            audio_content = audio_file.read()
            transcription = await transcription_service.transcribe(audio_content)
            print("✅ Transcribed audio file")

        # Process transcription into segments
        segments = text_processor.process_text(transcription)
        print("✅ Processed transcription into segments")

        # Generate embeddings for segments
        segment_embeddings = await embedding_service.generate_embeddings([seg.text for seg in segments])
        print("✅ Generated embeddings for segments")

        # Generate unique segment IDs and store in vector store
        segment_ids = [f"test_segment_{i}" for i in range(len(segments))]
        await vector_store.store_segments(segment_ids, segment_embeddings)
        print("✅ Stored segments in vector store")

        # Generate outline
        outline = await outline_service.generate_outline(segment_ids)
        print("✅ Generated outline")
        print(f"Outline: {outline}")

        # Clean up
        os.remove(test_audio_path)
        print("✅ Cleaned up test files")

        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_outline_generation()) 