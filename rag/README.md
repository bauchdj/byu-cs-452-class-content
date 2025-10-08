# RAG Embeddings Generator

This project generates embeddings for text data using different AI providers.

## Files

- `openai_embeddings.py`: Generates embeddings using OpenAI's API
- `google_embeddings.py`: Generates embeddings using Google's Vertex AI
- `free_embeddings.py`: Generates embeddings using Sentence Transformers (free)
- `config_loader.py`: Common module for loading configuration from `config.json`
- `base_embedding.py`: Common module with shared embedding functionality

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure API keys and models in `config.json`:
   - For OpenAI: Add your OpenAI API key
   - For Google: Add your Google Project ID
   - Embedding models for each provider can be configured in the config file

## Usage

Run any of the embedding scripts directly:

```bash
python openai_embeddings.py
python google_embeddings.py
python free_embeddings.py
```

Each script will process `SCRAPED_TALKS.csv` and `SCRAPED_PARAGRAPHS.csv` files and generate embeddings for the text content.
