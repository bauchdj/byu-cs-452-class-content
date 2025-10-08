import google.generativeai as genai
from config_loader import load_config, get_google_ai_key

# Load configuration
config = load_config()
google_ai_key = get_google_ai_key(config)

# Configure the SDK
genai.configure(api_key=google_ai_key)

# Test embedding generation with the correct model name
try:
    result = genai.embed_content(
        model='models/text-embedding-004',
        content='This is a test sentence for embedding.'
    )
    
    print("Successfully generated embedding using Google Generative AI SDK!")
    print(f"Embedding dimension: {len(result['embedding'])}")
    print(f"First 5 values: {result['embedding'][:5]}")
    
except Exception as e:
    print(f"Error testing Google Generative AI embeddings: {e}")
