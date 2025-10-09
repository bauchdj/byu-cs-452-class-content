import pandas as pd
import numpy as np
import ast
from sklearn.metrics.pairwise import cosine_similarity


def load_embedding_data(csv_file_path):
    """
    Load embedding data from CSV file (works with clusters, paragraphs, and talks).
    
    Args:
        csv_file_path (str): Path to the CSV file
    
    Returns:
        pandas.DataFrame: DataFrame with embedding data
    """
    df = pd.read_csv(csv_file_path)
    
    # Convert string embeddings to numpy arrays
    # Handle different embedding formats
    if 'embedding' in df.columns:
        df['embedding'] = df['embedding'].apply(lambda x: np.array(ast.literal_eval(x)))
    
    return df


def search_embeddings(query_embedding, df, top_k=5):
    """
    Perform semantic search on embedding data using a pre-computed query embedding.
    
    Args:
        query_embedding (numpy.ndarray): Pre-computed query embedding
        df (pandas.DataFrame): Data with embeddings
        top_k (int): Number of top results to return
    
    Returns:
        pandas.DataFrame: Top matching results
    """
    # Check if embedding column exists
    if 'embedding' not in df.columns:
        return pd.DataFrame()
    
    # Calculate cosine similarities
    embeddings = np.stack(df['embedding'].values)
    similarities = cosine_similarity([query_embedding], embeddings)[0]
    
    # Get top k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # Return top results
    results = df.iloc[top_indices].copy()
    results['similarity'] = similarities[top_indices]
    
    return results


def display_results(results, data_type="generic"):
    """
    Display search results in a readable format.
    
    Args:
        results (pandas.DataFrame): Search results
        data_type (str): Type of data (clusters, paragraphs, talks)
    """
    print(f"\nFound {len(results)} results:")
    print("=" * 80)
    
    for idx, row in results.iterrows():
        print(f"\nResult {idx + 1} (Similarity: {row['similarity']:.4f})")
        print(f"Title: {row['title']}")
        print(f"Speaker: {row['speaker']}")
        
        if 'calling' in row:
            print(f"Calling: {row['calling']}")
        
        if 'year' in row and 'season' in row:
            print(f"Year: {row['year']} {row['season']}")
        
        if 'cluster_id' in row:
            print(f"Cluster ID: {row['cluster_id']}")
        
        if 'paragraph_number' in row:
            print(f"Paragraph #: {row['paragraph_number']}")
        
        print(f"URL: {row['url']}")
        
        # Display text content
        if data_type == "clusters" and 'text' in row:
            # For clusters, text is a list of paragraphs
            try:
                paragraphs = ast.literal_eval(row['text'])
                print("Top paragraphs from cluster:")
                for i, paragraph in enumerate(paragraphs[:3]):  # Show top 3 paragraphs
                    print(f"  {i+1}. {paragraph[:200]}..." if len(paragraph) > 200 else f"  {i+1}. {paragraph}")
            except:
                print(f"Text: {row['text'][:200]}..." if len(row['text']) > 200 else f"Text: {row['text']}")
        elif 'text' in row:
            # For talks and paragraphs, text is a single string
            print(f"Text: {row['text'][:200]}..." if len(row['text']) > 200 else f"Text: {row['text']}")
        
        print("-" * 80)
