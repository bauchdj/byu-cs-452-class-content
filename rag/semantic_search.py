import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from config_loader import load_config, get_sentence_transformer_model, get_google_ai_key, get_google_embedding_model
import ast
import json
import pandas as pd

# TODO: make results easy to feed into AI
# then have AI answers the question
# then display the semantic search results with the AI generation (Retrieval w/ Generation)

def format_results_for_ai_generation(results, data_type):
    """
    Format search results specifically for AI generation.
    
    Args:
        results (pandas.DataFrame): Search results
        data_type (str): Type of data (clusters, paragraphs, talks)
    
    Returns:
        str: Formatted context string for AI generation
    """    
    context = ""
    
    for idx, row in results.iterrows():
        context += f"\nResult {idx + 1} (Similarity: {row['similarity']:.4f})\n"
        context += f"Title: {row['title']}\n"
        context += f"Speaker: {row['speaker']}\n"
        
        if 'year' in row and 'season' in row:
            context += f"Year: {row['year']} {row['season']}\n"
        
        # Add text content
        if data_type == "clusters" and 'text' in row:
            # For clusters, text is a list of paragraphs
            try:
                paragraphs = ast.literal_eval(row['text'])
                context += "Content:\n"
                for i, paragraph in enumerate(paragraphs[:3]):  # Show top 3 paragraphs
                    context += f"  {paragraph}\n"
            except:
                context += f"Content: {row['text']}\n"
        elif 'text' in row:
            # For talks and paragraphs, text is a single string
            context += f"Content: {row['text']}\n"
        
        context += "-" * 40 + "\n"
    
    return context

def generate_answer_with_context(query, context, model=None):
    """
    Generate an answer to a query using provided context.
    
    Args:
        query (str): The user's query
        context (str): Context information from semantic search results
        model: Google Generative AI model (if None, uses the global generation_model)
    
    Returns:
        str: Generated answer
    """
    if model is None:
        model = generation_model
    
    if model is None:
        return "Error: Google Generative AI model not configured for text generation."
    
    # Create the prompt
    prompt = f"""
You are a helpful assistant that answers questions based on provided context.

Context information:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information to answer the question, please state that clearly.
"""
    
    try:
        # Generate the response
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating answer: {e}"

def create_json_output(query, results, data_type, source, model_name, ai_answer):
    """
    Create JSON formatted output for analytics.
    
    Args:
        query (str): The search query
        results (pandas.DataFrame): Search results
        data_type (str): Type of data (clusters, paragraphs, talks)
        source (str): Data source (free or google_genai)
        model_name (str): Name of the model used
        ai_answer (str): AI generated answer
    
    Returns:
        dict: JSON serializable dictionary
    """
    # Convert DataFrame to list of dictionaries
    results_list = []
    for idx, row in results.iterrows():
        result_dict = {
            'rank': idx + 1,
            'similarity': float(row['similarity']),
            'title': row['title'],
            'speaker': row['speaker'],
            'url': row['url']
        }
        
        # Add optional fields if they exist
        if 'calling' in row:
            result_dict['calling'] = row['calling']
        if 'year' in row and 'season' in row:
            result_dict['year'] = row['year']
            result_dict['season'] = row['season']
        if 'cluster_id' in row:
            result_dict['cluster_id'] = row['cluster_id']
        if 'paragraph_number' in row:
            result_dict['paragraph_number'] = row['paragraph_number']
        
        # Add text content
        if data_type == "clusters" and 'text' in row:
            try:
                paragraphs = ast.literal_eval(row['text'])
                result_dict['text'] = paragraphs[:3]  # Top 3 paragraphs
            except:
                result_dict['text'] = row['text']
        elif 'text' in row:
            result_dict['text'] = row['text']
        
        results_list.append(result_dict)
    
    # Create the JSON output structure
    json_output = {
        'query': query,
        'model': model_name,
        'source': source,
        'data_type': data_type,
        'timestamp': pd.Timestamp.now().isoformat(),
        'result_count': len(results_list),
        'results': results_list,
        'ai_answer': ai_answer
    }
    
    return json_output

# Load the semantic search functions from our module
from semantic_search_generic import load_embedding_data, search_embeddings, display_results

# Load configuration
config = load_config()

# Configure Google Generative AI for text generation
try:
    google_ai_key = get_google_ai_key(config)
    genai.configure(api_key=google_ai_key)
    # Initialize the model for text generation
    generation_model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Warning: Could not configure Google Generative AI for text generation: {e}")
    generation_model = None

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

def semantic_search(output_file="semantic_search_results.txt", json_output_file="semantic_search_results.json"):
    """
    Example of how to perform semantic search on all embedding data using both SentenceTransformer and Google GenAI.
    
    Args:
        output_file (str): Path to output file for results
        json_output_file (str): Path to JSON output file for analytics
    """
    # Open output file
    with open(output_file, 'w') as f:
        f.write("SEMANTIC SEARCH RESULTS\n")
        f.write("=" * 50 + "\n\n")
    
    # Initialize JSON output file
    json_outputs = []
    with open(json_output_file, 'w') as f:
        json.dump([], f)
    
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
                        
                        # Generate AI answer using the context
                        context = format_results_for_ai_generation(results, data_type)
                        ai_answer = generate_answer_with_context(query, context)
                        
                        # Display AI answer
                        print(f"\nAI GENERATED ANSWER:")
                        print("=" * 40)
                        print(ai_answer)
                        print("=" * 40)
                        
                        # Create JSON output for analytics
                        json_output = create_json_output(query, results, data_type, source, "SentenceTransformer", ai_answer)
                        
                        # Write results to file
                        formatted_results = format_results_for_file(results, data_type, source, "SentenceTransformer", query)
                        with open(output_file, 'a') as f:
                            f.write(formatted_results)
                            f.write(f"\nAI GENERATED ANSWER:\n")
                            f.write("=" * 40 + "\n")
                            f.write(f"{ai_answer}\n")
                            f.write("=" * 40 + "\n\n")
                            # Write JSON output
                            f.write(f"\nJSON OUTPUT:\n")
                            f.write(json.dumps(json_output, indent=2) + "\n\n")
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
                        
                        # Generate AI answer using the context
                        context = format_results_for_ai_generation(results, data_type)
                        ai_answer = generate_answer_with_context(query, context)
                        
                        # Display AI answer
                        print(f"\nAI GENERATED ANSWER:")
                        print("=" * 40)
                        print(ai_answer)
                        print("=" * 40)
                        
                        # Create JSON output for analytics
                        json_output = create_json_output(query, results, data_type, source, "Google GenAI", ai_answer)
                        
                        # Write results to file
                        formatted_results = format_results_for_file(results, data_type, source, "Google GenAI", query)
                        with open(output_file, 'a') as f:
                            f.write(formatted_results)
                            f.write(f"\nAI GENERATED ANSWER:\n")
                            f.write("=" * 40 + "\n")
                            f.write(f"{ai_answer}\n")
                            f.write("=" * 40 + "\n\n")
                            # Write JSON output
                            f.write(f"\nJSON OUTPUT:\n")
                            f.write(json.dumps(json_output, indent=2) + "\n\n")
                    else:
                        print("  No results found.")
                        with open(output_file, 'a') as f:
                            f.write("  No results found.\n")
    
    # Write all JSON outputs to separate file
    with open(json_output_file, 'w') as f:
        json.dump(json_outputs, f, indent=2)
    
    print(f"\nResults have been saved to {output_file}")
    print(f"JSON analytics data has been saved to {json_output_file}")

if __name__ == "__main__":
    semantic_search()
