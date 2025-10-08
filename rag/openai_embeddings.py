from openai import OpenAI
import os
from config_loader import load_config, get_openai_key
from base_embedding import process_in_batches, process_csv_files

# Load configuration
config = load_config()
openai_key = get_openai_key(config)

client = OpenAI(api_key=openai_key)


def get_openai_embeddings(texts, model="text-embedding-3-small"):
    """
    Generate embeddings for a list of texts using OpenAI API.
    
    Args:
        texts: List of strings to embed
        model: Embedding model name
    
    Returns:
        List of embeddings
    """
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
        "openai"
    )

    