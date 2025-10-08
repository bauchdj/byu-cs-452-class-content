from openai import OpenAI
from config_loader import load_config, get_openai_key, get_openai_embedding_model
from base_embedding import process_in_batches, process_csv_files

# Load configuration
config = load_config()
openai_key = get_openai_key(config)
openai_model = get_openai_embedding_model(config)

client = OpenAI(api_key=openai_key)

def get_openai_embeddings(texts, model=None):
    """
    Generate embeddings for a list of texts using OpenAI API.
    
    Args:
        texts: List of strings to embed
        model: Embedding model name (if None, uses model from config)
    
    Returns:
        List of embeddings
    """
    if model is None:
        model = openai_model
    
    def process_batch(batch):
        response = client.embeddings.create(input=batch, model=model)
        return [item.embedding for item in response.data]
    
    return process_in_batches(texts, process_batch, model)

def process_openai_embeddings(texts):
    """
    Process texts and generate OpenAI embeddings.
    
    Args:
        texts: List of strings to embed
    
    Returns:
        List of embeddings
    """
    return get_openai_embeddings(texts)


if __name__ == "__main__":
    process_csv_files(
        "SCRAPED_TALKS.csv",
        "SCRAPED_PARAGRAPHS.csv",
        "openai",
        process_openai_embeddings,
        "openai",
        resume=True
    )
