import os
from dotenv import load_dotenv
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_embedding_and_vector_store():
    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    
    # Get embedding dimension
    vector_size = embedding_service.get_embedding_dimension()
    logger.info(f"Embedding dimension: {vector_size}")
    
    # Create collection if it doesn't exist
    try:
        vector_store.create_collection(vector_size)
        logger.info("Created new collection")
    except Exception as e:
        logger.info(f"Collection might already exist: {str(e)}")
    
    # Test data
    test_texts = [
        "The quick brown fox jumps over the lazy dog",
        "A fox is a clever and agile animal",
        "Dogs are known for their loyalty and companionship",
        "The weather is beautiful today",
        "I love programming and building software"
    ]
    
    # Generate embeddings
    embeddings = embedding_service.embed_texts(test_texts)
    logger.info(f"Generated embeddings shape: {embeddings.shape}")
    
    # Generate unique IDs for each segment
    segment_ids = [str(uuid.uuid4()) for _ in test_texts]
    
    # Add metadata
    metadata = [
        {"source": "test", "index": i} for i in range(len(test_texts))
    ]
    
    # Upsert to vector store
    vector_store.upsert_segments(
        segment_ids=segment_ids,
        vectors=embeddings,
        texts=test_texts,
        metadata=metadata
    )
    logger.info("Successfully upserted segments")
    
    # Test single segment retrieval
    test_id = segment_ids[0]
    segment = vector_store.get_segment_by_id(test_id)
    if segment:
        logger.info(f"Successfully retrieved segment by ID: {test_id}")
        logger.info(f"Segment text: {segment['text']}")
    else:
        logger.error(f"Failed to retrieve segment by ID: {test_id}")
    
    # Test batch segment retrieval
    segments = vector_store.get_segments_by_ids(segment_ids)
    logger.info(f"Retrieved {len(segments)} segments by IDs")
    
    # Test search
    query = "Tell me about foxes"
    query_embedding = embedding_service.embed_texts(query)
    results = vector_store.search_similar(
        query_vector=query_embedding,
        limit=2,
        score_threshold=0.5
    )
    
    logger.info("\nSearch results for query: %s", query)
    for result in results:
        logger.info(f"\nScore: {result['score']:.3f}")
        logger.info(f"Text: {result['text']}")
        logger.info(f"Metadata: {result.get('source')}, {result.get('index')}")

if __name__ == "__main__":
    test_embedding_and_vector_store() 