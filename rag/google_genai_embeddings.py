import google.generativeai as genai
from config_loader import load_config, get_google_embedding_model, get_google_ai_key
from base_embedding import process_in_batches, process_csv_files

try:
    # Load configuration
    config = load_config()
    
    # Get Google AI API key
    google_ai_key = get_google_ai_key(config)
    
    # Configure the SDK
    genai.configure(api_key=google_ai_key)
    
    # Get model name
    google_model = get_google_embedding_model(config)
    
    # Test the model to make sure it's available
    test_result = genai.embed_content(
        model=f'models/{google_model}',
        content='test'
    )
    
    print(f"Using Google Generative AI with model: {google_model}")
    
except Exception as e:
    print(f"Error initializing Google Generative AI: {e}")
    print("\nTo resolve this issue:")
    print("1. Make sure your config.json file contains a valid Google AI API key")
    print("2. Add your API key as 'googleAiKey' in config.json")
    print("3. Make sure the model specified in config.json is available in the Google Generative AI service")
    raise

def get_google_genai_embeddings(texts, model_name=None):
    """
    Generate embeddings for a list of texts using Google Generative AI.
    
    Args:
        texts: List of strings to embed
        model_name: Embedding model name (if None, uses model from config)
    
    Returns:
        List of embeddings
    """
    if model_name is None:
        model_name = google_model
    
    def process_batch(batch):
        # For Google Generative AI, we need to process each text individually
        # as the API doesn't support batch processing in the same way
        embeddings = []
        for text in batch:
            try:
                result = genai.embed_content(
                    model=f'models/{model_name}',
                    content=text
                )
                embeddings.append(result['embedding'])
            except Exception as e:
                print(f"Error generating embedding for text: {e}")
                # Return a zero vector of appropriate size as fallback
                embeddings.append([0.0] * 768)  # Standard size for many embedding models
        return embeddings
    
    return process_in_batches(texts, process_batch, model_name)

def process_google_genai_embeddings(texts):
    """
    Process texts and generate Google Generative AI embeddings.
    
    Args:
        texts: List of strings to embed
    
    Returns:
        List of embeddings
    """
    return get_google_genai_embeddings(texts)

if __name__ == "__main__":
    process_csv_files(
        "SCRAPED_TALKS.csv",
        "SCRAPED_PARAGRAPHS.csv",
        "google_genai",
        process_google_genai_embeddings,
        "google_genai",
        resume=True,
        chunk_size=100
    )
