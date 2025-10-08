import pandas as pd
import tiktoken
from datetime import datetime
import json
import os
import vertexai
from vertexai.language_models import TextEmbeddingModel

# Load configuration
with open("config.json") as config:
    config_data = json.load(config)
    google_project_id = config_data.get("googleProjectId", "your-google-project-id")

# Initialize Vertex AI
vertexai.init(project=google_project_id, location="us-central1")

# Initialize the model
model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")

def get_embedding(texts, output_dir, model_name="textembedding-gecko@003", max_tokens=300000):
    """
    Generate embeddings for a list of texts in batches, respecting token limits.
    
    Args:
        texts: List of strings to embed
        output_dir: Directory to save output files
        model_name: Embedding model name
        max_tokens: Maximum tokens per API request
    
    Returns:
        List of embeddings
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize tokenizer (using OpenAI's tokenizer as approximation)
    encoder = tiktoken.encoding_for_model("text-embedding-3-small")
    
    # Clean texts and calculate token counts
    texts = [text.replace("\n", " ") for text in texts]
    token_counts = [len(encoder.encode(text)) for text in texts]
    
    embeddings = []
    current_batch = []
    current_token_count = 0
    
    for i, (text, token_count) in enumerate(zip(texts, token_counts)):
        if current_token_count + token_count > max_tokens or len(current_batch) >= 100:
            # Process current batch
            response = model.get_embeddings(current_batch)
            batch_embeddings = [item.values for item in response]
            embeddings.extend(batch_embeddings)
            # Reset batch
            current_batch = [text]
            current_token_count = token_count
        else:
            current_batch.append(text)
            current_token_count += token_count
    
    # Process final batch
    if current_batch:
        response = model.get_embeddings(current_batch)
        batch_embeddings = [item.values for item in response]
        embeddings.extend(batch_embeddings)
    
    return embeddings

if __name__ == "__main__":
    output_dir = "google"

    # Process talks.csv
    df = pd.read_csv("SCRAPED_TALKS.csv")
    df['embedding'] = get_embedding(df['text'].tolist(), output_dir, model_name='textembedding-gecko@003')
    output_talks = os.path.join(output_dir, 'google_talks.csv')
    df.to_csv(output_talks, index=False)

    # Process paragraphs.csv
    df = pd.read_csv("SCRAPED_PARAGRAPHS.csv")
    df['embedding'] = get_embedding(df['text'].tolist(), output_dir, model_name='textembedding-gecko@003')
    output_paragraphs = os.path.join(output_dir, 'google_paragraphs.csv')
    df.to_csv(output_paragraphs, index=False)

    file_to_delete = "SCRAPED_TALKS.csv"
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)
        print(f"Deleted file: {file_to_delete}")
    file_to_delete = "SCRAPED_PARAGRAPHS.csv"
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)
        print(f"Deleted file: {file_to_delete}")
