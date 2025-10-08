import pandas as pd
import tiktoken
import os


def prepare_texts_and_tokens(texts, model_name):
    """
    Prepare texts and calculate token counts.
    
    Args:
        texts: List of strings to embed
        model_name: Name of the model to use for tokenization
    
    Returns:
        tuple: (cleaned_texts, token_counts)
    """
    # Clean texts
    cleaned_texts = [text.replace("\n", " ") for text in texts]
    
    # Initialize tokenizer
    try:
        encoder = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to a default model if the specified one is not found
        encoder = tiktoken.encoding_for_model("text-embedding-3-small")
    
    # Calculate token counts
    token_counts = [len(encoder.encode(text)) for text in cleaned_texts]
    
    return cleaned_texts, token_counts


def process_in_batches(texts, process_batch_func, model_name="text-embedding-3-small", max_tokens=300000, max_batch_size=100):
    """
    Process texts in batches, respecting token limits.
    
    Args:
        texts: List of strings to embed
        process_batch_func: Function to process a batch of texts
        model_name: Name of the model to use for tokenization
        max_tokens: Maximum tokens per API request
        max_batch_size: Maximum number of texts per batch
    
    Returns:
        List of embeddings
    """
    # Prepare texts and calculate token counts
    cleaned_texts, token_counts = prepare_texts_and_tokens(texts, model_name)
    
    embeddings = []
    current_batch = []
    current_token_count = 0
    
    for i, (text, token_count) in enumerate(zip(cleaned_texts, token_counts)):
        if current_token_count + token_count > max_tokens or len(current_batch) >= max_batch_size:
            # Process current batch
            batch_embeddings = process_batch_func(current_batch)
            embeddings.extend(batch_embeddings)
            # Reset batch
            current_batch = [text]
            current_token_count = token_count
        else:
            current_batch.append(text)
            current_token_count += token_count
    
    # Process final batch
    if current_batch:
        batch_embeddings = process_batch_func(current_batch)
        embeddings.extend(batch_embeddings)
    
    return embeddings

def process_all_at_once(texts, process_func):
    """
    Process all texts at once with models that handle batching internally.
    
    Args:
        texts: List of strings to embed
        process_func: Function to process all texts at once
    
    Returns:
        List of embeddings
    """
    # Clean texts
    cleaned_texts = [text.replace("\n", " ") for text in texts]
    
    # Process all texts at once
    embeddings = process_func(cleaned_texts)
    
    return embeddings

def save_embeddings_to_csv(texts, embeddings, output_file):
    """
    Save texts and their embeddings to a CSV file.
    
    Args:
        texts: List of original texts
        embeddings: List of embeddings
        output_file: Path to the output CSV file
    """
    df = pd.DataFrame({
        'text': texts,
        'embedding': embeddings
    })
    df.to_csv(output_file, index=False)
    

def process_csv_files(input_talks_file, input_paragraphs_file, output_dir, process_func, prefix, resume=True):
    """
    Process CSV files and generate embeddings.
    
    Args:
        input_talks_file: Path to the talks CSV file
        input_paragraphs_file: Path to the paragraphs CSV file
        output_dir: Directory to save output files
        process_func: Function to process texts and generate embeddings
        prefix: Prefix for output files
        resume: Whether to resume from existing output files if they exist
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    files_processed = 0
    
    # Process talks.csv
    if os.path.exists(input_talks_file):
        df_talks = pd.read_csv(input_talks_file)
        output_talks = os.path.join(output_dir, f'{prefix}_talks.csv')
        
        # Check if we should resume from existing output
        if resume and os.path.exists(output_talks):
            print(f"Resuming from existing {output_talks}")
            df_output_talks = pd.read_csv(output_talks)
            processed_count = len(df_output_talks)
            total_count = len(df_talks)
            
            if processed_count < total_count:
                print(f"Resuming talks processing from record {processed_count}/{total_count}")
                remaining_texts = df_talks['text'].tolist()[processed_count:]
                remaining_embeddings = process_func(remaining_texts)
                
                # Combine existing and new embeddings
                all_embeddings = df_output_talks['embedding'].tolist() + remaining_embeddings
                df_talks['embedding'] = all_embeddings
                df_talks.to_csv(output_talks, index=False)
                print(f"Saved talks embeddings to {output_talks}")
            else:
                print(f"Talks processing already complete ({processed_count} records)")
                df_talks = df_output_talks  # Use existing data
        else:
            talks_embeddings = process_func(df_talks['text'].tolist())
            df_talks['embedding'] = talks_embeddings
            df_talks.to_csv(output_talks, index=False)
            print(f"Saved talks embeddings to {output_talks}")
        
        files_processed += 1
    else:
        print(f"Warning: {input_talks_file} not found, skipping...")
    
    # Process paragraphs.csv
    if os.path.exists(input_paragraphs_file):
        df_paragraphs = pd.read_csv(input_paragraphs_file)
        output_paragraphs = os.path.join(output_dir, f'{prefix}_paragraphs.csv')
        
        # Check if we should resume from existing output
        if resume and os.path.exists(output_paragraphs):
            print(f"Resuming from existing {output_paragraphs}")
            df_output_paragraphs = pd.read_csv(output_paragraphs)
            processed_count = len(df_output_paragraphs)
            total_count = len(df_paragraphs)
            
            if processed_count < total_count:
                print(f"Resuming paragraphs processing from record {processed_count}/{total_count}")
                remaining_texts = df_paragraphs['text'].tolist()[processed_count:]
                remaining_embeddings = process_func(remaining_texts)
                
                # Combine existing and new embeddings
                all_embeddings = df_output_paragraphs['embedding'].tolist() + remaining_embeddings
                df_paragraphs['embedding'] = all_embeddings
                df_paragraphs.to_csv(output_paragraphs, index=False)
                print(f"Saved paragraphs embeddings to {output_paragraphs}")
            else:
                print(f"Paragraphs processing already complete ({processed_count} records)")
                df_paragraphs = df_output_paragraphs  # Use existing data
        else:
            paragraphs_embeddings = process_func(df_paragraphs['text'].tolist())
            df_paragraphs['embedding'] = paragraphs_embeddings
            df_paragraphs.to_csv(output_paragraphs, index=False)
            print(f"Saved paragraphs embeddings to {output_paragraphs}")
        
        files_processed += 1
    else:
        print(f"Warning: {input_paragraphs_file} not found, skipping...")
    
    if files_processed == 0:
        print("No input files found. Please make sure SCRAPED_TALKS.csv and/or SCRAPED_PARAGRAPHS.csv exist.")
        return
    
    # Delete input files
    # for file_to_delete in [input_talks_file, input_paragraphs_file]:
    #     if os.path.exists(file_to_delete):
    #         os.remove(file_to_delete)
    #         print(f"Deleted file: {file_to_delete}")
