# RAG Embeddings Generator

This project generates embeddings for text data using different AI providers.

## Files

- `openai_embeddings.py`: Generates embeddings using OpenAI's API
- `google_embeddings.py`: Generates embeddings using Google's Vertex AI
- `google_genai_embeddings.py`: Generates embeddings using Google's Generative AI (API key)
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

3. For Google Cloud authentication, you need to set up Application Default Credentials (ADC):
   - Install the Google Cloud CLI: https://cloud.google.com/sdk/docs/install
   - Run `gcloud auth application-default login` to authenticate
   - Or set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account key file

4. Copy `config_template.json` to `config.json` and fill in your credentials:

## Usage

Run any of the embedding scripts directly:

```bash
python openai_embeddings.py
python google_embeddings.py
python google_genai_embeddings.py
python free_embeddings.py
```

Each script will process `SCRAPED_TALKS.csv` and `SCRAPED_PARAGRAPHS.csv` files and generate embeddings for the text content.
