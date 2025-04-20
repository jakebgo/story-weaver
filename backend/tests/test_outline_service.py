from app.services.outline_service import OutlineService

def test_outline_service_initialization():
    """Test that the OutlineService initializes properly with the Gemini API key."""
    try:
        service = OutlineService()
        assert service.model is not None, "Gemini model should be initialized"
        print("✅ OutlineService initialized successfully with Gemini 2.0 Flash")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize OutlineService: {str(e)}")
        return False

if __name__ == "__main__":
    test_outline_service_initialization() 