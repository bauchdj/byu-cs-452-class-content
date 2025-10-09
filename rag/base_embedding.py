import pandas as pd
import tiktoken
import os
from tqdm import tqdm


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
    
    # Initialize progress bar
    pbar = tqdm(total=len(cleaned_texts), desc="Processing texts")
    
    for i, (text, token_count) in enumerate(zip(cleaned_texts, token_counts)):
        if current_token_count + token_count > max_tokens or len(current_batch) >= max_batch_size:
            # Process current batch
            batch_embeddings = process_batch_func(current_batch)
            embeddings.extend(batch_embeddings)
            # Update progress bar
            pbar.update(len(current_batch))
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
        # Update progress bar for final batch
        pbar.update(len(current_batch))
    
    # Close progress bar
    pbar.close()
    
    return embeddings
def process_all_at_once(texts, process_func):
    """
    Process all texts at once with models that handle batching internally.
    
{{ ... }}
        texts: List of strings to embed
        process_func: Function to process all texts at once
    
    Returns:
        List of embeddings
    """
    # Clean texts
    cleaned_texts = [text.replace("\n", " ") for text in texts]
    
    # Initialize progress bar
    pbar = tqdm(total=1, desc="Processing all texts")
    
    # Process all texts at once
    embeddings = process_func(cleaned_texts)
    
    # Update and close progress bar
    pbar.update(1)
    pbar.close()
    
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
    

def process_csv_files(input_talks_file, input_paragraphs_file, output_dir, process_func, prefix, resume=True, chunk_size=100):
    """
    Process CSV files and generate embeddings with incremental saving.
    
    Args:
        input_talks_file: Path to the talks CSV file
        input_paragraphs_file: Path to the paragraphs CSV file
        output_dir: Directory to save output files
        process_func: Function to process texts and generate embeddings
        prefix: Prefix for output files
        resume: Whether to resume from existing output files if they exist
        chunk_size: Number of texts to process before saving
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
                # Process in chunks with incremental saving
                texts = df_talks['text'].tolist()
                all_embeddings = df_output_talks['embedding'].tolist() if 'embedding' in df_output_talks.columns else []
                
                # Progress bar for remaining texts
                pbar = tqdm(total=total_count, desc="Processing talks", initial=processed_count)
                
                # Process remaining texts in chunks
                for i in range(processed_count, total_count, chunk_size):
                    chunk_end = min(i + chunk_size, total_count)
                    chunk_texts = texts[i:chunk_end]
                    chunk_embeddings = process_func(chunk_texts)
                    all_embeddings.extend(chunk_embeddings)
                    
                    # Update progress bar
                    pbar.update(len(chunk_texts))
                    
                    # Save progress incrementally
                    df_talks_partial = df_talks.copy()
                    df_talks_partial['embedding'] = all_embeddings + [None] * (len(df_talks_partial) - len(all_embeddings))
                    # Only keep rows that have embeddings
                    df_talks_partial = df_talks_partial.iloc[:len(all_embeddings)]
                    df_talks_partial.to_csv(output_talks, index=False)
                
                pbar.close()
                
                # Final save with all embeddings
                df_talks['embedding'] = all_embeddings
                df_talks.to_csv(output_talks, index=False)
                print(f"Saved talks embeddings to {output_talks}")
            else:
                print(f"Talks processing already complete ({processed_count} records)")
                df_talks = df_output_talks  # Use existing data
        else:
            # Process all texts in chunks with incremental saving
            texts = df_talks['text'].tolist()
            total_count = len(texts)
            all_embeddings = []
            
            # Progress bar for all texts
            pbar = tqdm(total=total_count, desc="Processing talks")
            
            # Process texts in chunks
            for i in range(0, total_count, chunk_size):
                chunk_end = min(i + chunk_size, total_count)
                chunk_texts = texts[i:chunk_end]
                chunk_embeddings = process_func(chunk_texts)
                all_embeddings.extend(chunk_embeddings)
                
                # Update progress bar
                pbar.update(len(chunk_texts))
                
                # Save progress incrementally
                df_talks_partial = df_talks.copy()
                df_talks_partial['embedding'] = all_embeddings + [None] * (len(df_talks_partial) - len(all_embeddings))
                # Only keep rows that have embeddings
                df_talks_partial = df_talks_partial.iloc[:len(all_embeddings)]
                df_talks_partial.to_csv(output_talks, index=False)
            
            pbar.close()
            
            # Final save with all embeddings
            df_talks['embedding'] = all_embeddings
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
                # Process in chunks with incremental saving
                texts = df_paragraphs['text'].tolist()
                all_embeddings = df_output_paragraphs['embedding'].tolist() if 'embedding' in df_output_paragraphs.columns else []
                
                # Progress bar for remaining texts
                pbar = tqdm(total=total_count, desc="Processing paragraphs", initial=processed_count)
                
                # Process remaining texts in chunks
                for i in range(processed_count, total_count, chunk_size):
                    chunk_end = min(i + chunk_size, total_count)
                    chunk_texts = texts[i:chunk_end]
                    chunk_embeddings = process_func(chunk_texts)
                    all_embeddings.extend(chunk_embeddings)
                    
                    # Update progress bar
                    pbar.update(len(chunk_texts))
                    
                    # Save progress incrementally
                    df_paragraphs_partial = df_paragraphs.copy()
                    df_paragraphs_partial['embedding'] = all_embeddings + [None] * (len(df_paragraphs_partial) - len(all_embeddings))
                    # Only keep rows that have embeddings
                    df_paragraphs_partial = df_paragraphs_partial.iloc[:len(all_embeddings)]
                    df_paragraphs_partial.to_csv(output_paragraphs, index=False)
                
                pbar.close()
                
                # Final save with all embeddings
                df_paragraphs['embedding'] = all_embeddings
                df_paragraphs.to_csv(output_paragraphs, index=False)
                print(f"Saved paragraphs embeddings to {output_paragraphs}")
            else:
                print(f"Paragraphs processing already complete ({processed_count} records)")
                df_paragraphs = df_output_paragraphs  # Use existing data
        else:
            # Process all texts in chunks with incremental saving
            texts = df_paragraphs['text'].tolist()
            total_count = len(texts)
            all_embeddings = []
            
            # Progress bar for all texts
            pbar = tqdm(total=total_count, desc="Processing paragraphs")
            
            # Process texts in chunks
            for i in range(0, total_count, chunk_size):
                chunk_end = min(i + chunk_size, total_count)
                chunk_texts = texts[i:chunk_end]
                chunk_embeddings = process_func(chunk_texts)
                all_embeddings.extend(chunk_embeddings)
                
                # Update progress bar
                pbar.update(len(chunk_texts))
                
                # Save progress incrementally
                df_paragraphs_partial = df_paragraphs.copy()
                df_paragraphs_partial['embedding'] = all_embeddings + [None] * (len(df_paragraphs_partial) - len(all_embeddings))
                # Only keep rows that have embeddings
                df_paragraphs_partial = df_paragraphs_partial.iloc[:len(all_embeddings)]
                df_paragraphs_partial.to_csv(output_paragraphs, index=False)
            
            pbar.close()
            
            # Final save with all embeddings
            df_paragraphs['embedding'] = all_embeddings
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
