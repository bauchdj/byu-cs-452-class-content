import vertexai
from vertexai.language_models import TextEmbeddingModel
from config_loader import load_config, get_google_project_id, get_google_embedding_model
from base_embedding import process_in_batches, process_csv_files

# Load configuration
config = load_config()
google_project_id = get_google_project_id(config)
google_model = get_google_embedding_model(config)

# Initialize Vertex AI
vertexai.init(project=google_project_id, location="us-central1")

# Initialize the model
model = TextEmbeddingModel.from_pretrained(google_model)

def get_google_embeddings(texts, model_name=None):
    """
    Generate embeddings for a list of texts using Google Vertex AI.
    
    Args:
        texts: List of strings to embed
        model_name: Embedding model name (if None, uses model from config)
    
    Returns:
        List of embeddings
    """
    if model_name is None:
        model_name = google_model
    
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
