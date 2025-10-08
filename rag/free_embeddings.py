import pandas as pd
from sentence_transformers import SentenceTransformer
import torch
import os
from base_embedding import process_csv_files, process_all_at_once


def get_free_embeddings(texts):
    """
    Generate embeddings for a list of texts using Sentence Transformers.
    
    Args:
        texts: List of strings to embed
    
    Returns:
        List of embeddings
    """
    # Initialize the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Move model to GPU if available
    if torch.cuda.is_available():
        model = model.to('cuda')
        print("Using GPU for encoding")
    else:
        print("Using CPU for encoding")

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).tolist()

    return embeddings


def process_free_embeddings(texts):
    """
    Process texts and generate free embeddings.
    
    Args:
        texts: List of strings to embed
    
    Returns:
        List of embeddings
    """
    return process_all_at_once(texts, get_free_embeddings)


if __name__ == "__main__":
    process_csv_files(
        "SCRAPED_TALKS.csv",
        "SCRAPED_PARAGRAPHS.csv",
        "free",
        process_free_embeddings,
        "free"
    )