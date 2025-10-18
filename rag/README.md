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

## Resume Functionality

All embedding scripts now support resuming from where they left off. If an output file already exists, the script will check how many records have been processed and resume from that point. This is particularly useful if the process was interrupted and you want to continue rather than start over.

## Clustering

After generating embeddings, you can cluster the paragraph embeddings to group similar content:

```bash
python clusters.py
```

This will generate cluster embeddings for each talk using k-means clustering.

## Semantic Search on All Embedding Data

To perform semantic search on all embedding CSV files (clusters, paragraphs, and talks) for both free and Google GenAI models:

1. Use the example script that demonstrates searching across all data types:
   ```bash
   python semantic_search.py
   ```

   This will save the results to `semantic_search_results.txt`.

2. Or use the Python API directly:
   ```python
   import numpy as np
   from sentence_transformers import SentenceTransformer
   import google.generativeai as genai
   from config_loader import load_config, get_google_ai_key, get_google_embedding_model
   from semantic_search_generic import load_embedding_data, search_embeddings, display_results
   
   # Load data from different sources and types
   df_clusters = load_embedding_data('free/free_3_clusters.csv')
   df_paragraphs = load_embedding_data('free/free_paragraphs.csv')
   df_talks = load_embedding_data('free/free_talks.csv')
   
   # Method 1: Using Sentence Transformer
   model = SentenceTransformer('all-MiniLM-L6-v2')
   query_embedding = model.encode(["faith and family"])[0]
   
   # Search across all data types
   results_clusters = search_embeddings(query_embedding, df_clusters, top_k=3)
   results_paragraphs = search_embeddings(query_embedding, df_paragraphs, top_k=3)
   results_talks = search_embeddings(query_embedding, df_talks, top_k=3)
   
   # Display results
   display_results(results_clusters, "clusters")
   display_results(results_paragraphs, "paragraphs")
   display_results(results_talks, "talks")
   
   # Method 2: Using Google GenAI
   config = load_config()
   google_ai_key = get_google_ai_key(config)
   genai.configure(api_key=google_ai_key)
   model_name = get_google_embedding_model(config)
   
   result = genai.embed_content(
       model=f'models/{model_name}',
       content="faith and family"
   )
   query_embedding = np.array(result['embedding'])
   
   # Search across all data types
   results_clusters = search_embeddings(query_embedding, df_clusters, top_k=3)
   results_paragraphs = search_embeddings(query_embedding, df_paragraphs, top_k=3)
   results_talks = search_embeddings(query_embedding, df_talks, top_k=3)
   
   # Display results
   display_results(results_clusters, "clusters")
   display_results(results_paragraphs, "paragraphs")
   display_results(results_talks, "talks")
   ```

The new generic semantic search implementation can work with all CSV files (clusters, paragraphs, and talks) from both free and Google GenAI embedding sources. The example `semantic_search.py` script demonstrates how to use both SentenceTransformer and Google GenAI models to generate embeddings and then perform semantic search across all data types. Results are automatically saved to `semantic_search_results.txt`.

You can also specify a custom output file:
```python
from semantic_search import semantic_search
semantic_search("my_custom_results.txt")
```
