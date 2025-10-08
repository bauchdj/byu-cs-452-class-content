import os
import vertexai
from vertexai.language_models import TextEmbeddingModel
from config_loader import load_config, get_google_project_id
from base_embedding import process_in_batches, process_csv_files

# Load configuration
config = load_config()
google_project_id = get_google_project_id(config)

# Initialize Vertex AI
vertexai.init(project=google_project_id, location="us-central1")

# Initialize the model
model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")


def get_google_embeddings(texts, model_name="textembedding-gecko@003"):
    """
    Generate embeddings for a list of texts using Google Vertex AI.
    
    Args:
        texts: List of strings to embed
        model_name: Embedding model name
    
    Returns:
        List of embeddings
    """
    def process_batch(batch):
        response = model.get_embeddings(batch)
        return [item.values for item in response]
    
    return process_in_batches(texts, process_batch, model_name)


def process_google_embeddings(texts):
    """
    Process texts and generate Google embeddings.
    
    Args:
        texts: List of strings to embed
    
    Returns:
        List of embeddings
    """
    return get_google_embeddings(texts)


if __name__ == "__main__":
    process_csv_files(
        "SCRAPED_TALKS.csv",
        "SCRAPED_PARAGRAPHS.csv",
        "google",
        process_google_embeddings,
        "google"
    )
