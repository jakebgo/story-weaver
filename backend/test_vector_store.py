import os
from dotenv import load_dotenv
from app.ai import EmbeddingService, VectorStore
import uuid

# Load environment variables
load_dotenv()

def test_embedding_and_vector_store():
    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    
    # Get embedding dimension
    vector_size = embedding_service.get_embedding_dimension()
    print(f"Embedding dimension: {vector_size}")
    
    # Create collection if it doesn't exist
    try:
        vector_store.create_collection(vector_size)
        print("Created new collection")
    except Exception as e:
        print(f"Collection might already exist: {str(e)}")
    
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
    print(f"Generated embeddings shape: {embeddings.shape}")
    
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
    print("Successfully upserted segments")
    
    # Test search
    query = "Tell me about foxes"
    query_embedding = embedding_service.embed_text(query)
    results = vector_store.search_similar(
        query_vector=query_embedding,
        limit=2,
        score_threshold=0.5
    )
    
    print("\nSearch results for query:", query)
    for result in results:
        print(f"\nScore: {result['score']:.3f}")
        print(f"Text: {result['text']}")
        print(f"Metadata: {result.get('source')}, {result.get('index')}")

if __name__ == "__main__":
    test_embedding_and_vector_store() 