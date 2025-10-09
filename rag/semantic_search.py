import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from config_loader import load_config, get_sentence_transformer_model, get_google_ai_key, get_google_embedding_model
import ast

# Load the semantic search functions from our module
from semantic_search_generic import load_embedding_data, search_embeddings, display_results

# Load configuration
config = load_config()

queries = [
    "How can I gain a testimony of Jesus Christ?",
    "What are some ways to deal with challenges in life and find a purpose?",
    "How can I fix my car if it won't start?",
    "Why did dinosaurs exist?",
    "How can I prepare for the second coming of Jesus Christ?",
]

def get_sentence_transformer_embeddings(texts):
    """
    Generate embeddings using Sentence Transformer model.
    """
    sentence_transformer_model = get_sentence_transformer_model(config)
    model = SentenceTransformer(sentence_transformer_model)
    embeddings = model.encode(texts)
    return embeddings

def get_google_genai_embeddings(texts, model_name=None):
    """
    Generate embeddings using Google Generative AI.
    """
    # Get Google AI API key
    google_ai_key = get_google_ai_key(config)
    
    # Configure the SDK
    genai.configure(api_key=google_ai_key)
    
    # Get model name
    if model_name is None:
        model_name = get_google_embedding_model(config)
    
    # Generate embeddings
    embeddings = []
    for text in texts:
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
    
    return np.array(embeddings)

def format_results_for_file(results, data_type, source, model_name, query):
    """
    Format results for writing to a file.
    
    Args:
        results (pandas.DataFrame): Search results
        data_type (str): Type of data (clusters, paragraphs, talks)
        source (str): Data source (free or google_genai)
        model_name (str): Name of the model used
        query (str): The search query
    
    Returns:
        str: Formatted results string
    """
    output = f"\nQUERY: {query}\n"
    output += f"MODEL: {model_name}\n"
    output += f"SOURCE: {source}\n"
    output += f"DATA TYPE: {data_type}\n"
    output += f"FOUND {len(results)} RESULTS:\n"
    output += "=" * 80 + "\n"
    
    for idx, row in results.iterrows():
        output += f"\nResult {idx + 1} (Similarity: {row['similarity']:.4f})\n"
        output += f"Title: {row['title']}\n"
        output += f"Speaker: {row['speaker']}\n"
        
        if 'calling' in row:
            output += f"Calling: {row['calling']}\n"
        
        if 'year' in row and 'season' in row:
            output += f"Year: {row['year']} {row['season']}\n"
        
        if 'cluster_id' in row:
            output += f"Cluster ID: {row['cluster_id']}\n"
        
        if 'paragraph_number' in row:
            output += f"Paragraph #: {row['paragraph_number']}\n"
        
        output += f"URL: {row['url']}\n"
        
        # Add text content
        if data_type == "clusters" and 'text' in row:
            # For clusters, text is a list of paragraphs
            try:
                paragraphs = ast.literal_eval(row['text'])
                output += "Top paragraphs from cluster:\n"
                for i, paragraph in enumerate(paragraphs[:3]):  # Show top 3 paragraphs
                    output += f"  {i+1}. {paragraph[:200]}...\n" if len(paragraph) > 200 else f"  {i+1}. {paragraph}\n"
            except:
                output += f"Text: {row['text'][:200]}...\n" if len(row['text']) > 200 else f"Text: {row['text']}\n"
        elif 'text' in row:
            # For talks and paragraphs, text is a single string
            output += f"Text: {row['text'][:200]}...\n" if len(row['text']) > 200 else f"Text: {row['text']}\n"
        
        output += "-" * 80 + "\n"
    
    return output

def semantic_search(output_file="semantic_search_results.txt"):
    """
    Example of how to perform semantic search on all embedding data using both SentenceTransformer and Google GenAI.
    
    Args:
        output_file (str): Path to output file for results
    """
    # Open output file
    with open(output_file, 'w') as f:
        f.write("SEMANTIC SEARCH RESULTS\n")
        f.write("=" * 50 + "\n\n")
    
    # Define file paths for both free and google_genai
    data_files = {
        'free': {
            'clusters': 'free/free_3_clusters.csv',
            'paragraphs': 'free/free_paragraphs.csv',
            'talks': 'free/free_talks.csv'
        },
        'google_genai': {
            'clusters': 'google_genai/google_genai_3_clusters.csv',
            'paragraphs': 'google_genai/google_genai_paragraphs.csv',
            'talks': 'google_genai/google_genai_talks.csv'
        }
    }
    
    # Load all data
    print("Loading all embedding data...")
    with open(output_file, 'a') as f:
        f.write("Loading all embedding data...\n")
    
    loaded_data = {}
    
    for source, files in data_files.items():
        loaded_data[source] = {}
        for data_type, file_path in files.items():
            try:
                loaded_data[source][data_type] = load_embedding_data(file_path)
                print(f"Loaded {len(loaded_data[source][data_type])} {data_type} embeddings from {source}")
                with open(output_file, 'a') as f:
                    f.write(f"Loaded {len(loaded_data[source][data_type])} {data_type} embeddings from {source}\n")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                with open(output_file, 'a') as f:
                    f.write(f"Error loading {file_path}: {e}\n")
                loaded_data[source][data_type] = None
    
    print("\nRUNNING QUERIES WITH SENTENCE TRANSFORMER MODEL")
    print("="*60)
    with open(output_file, 'a') as f:
        f.write("\nRUNNING QUERIES WITH SENTENCE TRANSFORMER MODEL\n")
        f.write("="*60 + "\n")
    
    for query in queries:
        print(f"\n{'='*100}")
        print(f"SEARCHING FOR: '{query}'")
        print(f"{'='*100}")
        with open(output_file, 'a') as f:
            f.write(f"\n{'='*100}\n")
            f.write(f"SEARCHING FOR: '{query}'\n")
            f.write(f"{'='*100}\n")
        
        # Generate embedding using Sentence Transformer
        query_embedding = get_sentence_transformer_embeddings([query])[0]
        
        # Perform semantic search on all data types for both sources
        for source, data_dict in loaded_data.items():
            print(f"\n--- Results from {source.upper()} ---")
            with open(output_file, 'a') as f:
                f.write(f"\n--- Results from {source.upper()} ---\n")
            
            for data_type, df in data_dict.items():
                if df is not None:
                    print(f"\n{data_type.upper()}:")
                    results = search_embeddings(query_embedding, df, top_k=3)
                    if not results.empty:
                        display_results(results, data_type)
                        # Write results to file
                        formatted_results = format_results_for_file(results, data_type, source, "SentenceTransformer", query)
                        with open(output_file, 'a') as f:
                            f.write(formatted_results)
                    else:
                        print("  No results found.")
                        with open(output_file, 'a') as f:
                            f.write("  No results found.\n")
    
    print("\nRUNNING QUERIES WITH GOOGLE GENAI MODEL")
    print("="*60)
    with open(output_file, 'a') as f:
        f.write("\nRUNNING QUERIES WITH GOOGLE GENAI MODEL\n")
        f.write("="*60 + "\n")
    
    for query in queries:
        print(f"\n{'='*100}")
        print(f"SEARCHING FOR: '{query}'")
        print(f"{'='*100}")
        with open(output_file, 'a') as f:
            f.write(f"\n{'='*100}\n")
            f.write(f"SEARCHING FOR: '{query}'\n")
            f.write(f"{'='*100}\n")
        
        # Generate embedding using Google GenAI
        query_embedding = get_google_genai_embeddings([query])[0]
        
        # Perform semantic search on all data types for both sources
        for source, data_dict in loaded_data.items():
            print(f"\n--- Results from {source.upper()} ---")
            with open(output_file, 'a') as f:
                f.write(f"\n--- Results from {source.upper()} ---\n")
            
            for data_type, df in data_dict.items():
                if df is not None:
                    print(f"\n{data_type.upper()}:")
                    results = search_embeddings(query_embedding, df, top_k=3)
                    if not results.empty:
                        display_results(results, data_type)
                        # Write results to file
                        formatted_results = format_results_for_file(results, data_type, source, "Google GenAI", query)
                        with open(output_file, 'a') as f:
                            f.write(formatted_results)
                    else:
                        print("  No results found.")
                        with open(output_file, 'a') as f:
                            f.write("  No results found.\n")
    
    print(f"\nResults have been saved to {output_file}")

if __name__ == "__main__":
    semantic_search()
