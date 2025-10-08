import json
import os

def load_config(config_path="config.json"):
    """
    Load configuration from config.json file.
    
    Args:
        config_path (str): Path to the configuration file
    
    Returns:
        dict: Configuration data
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found. Please create it first.")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

def get_openai_key(config):
    """
    Get OpenAI API key from configuration.
    
    Args:
        config (dict): Configuration data
    
    Returns:
        str: OpenAI API key
    """
    openai_key = config.get("openaiKey")
    if not openai_key or openai_key == "insert your OpenAI API key here":
        raise ValueError("OpenAI API key not found in config.json. Please add your API key.")
    return openai_key

def get_google_project_id(config):
    """
    Get Google Project ID from configuration.
    
    Args:
        config (dict): Configuration data
    
    Returns:
        str: Google Project ID
    """
    project_id = config.get("googleProjectId")
    if not project_id or project_id == "insert your Google Project ID here":
        raise ValueError("Google Project ID not found in config.json. Please add your Project ID.")
    return project_id

def get_openai_embedding_model(config):
    """
    Get OpenAI embedding model from configuration.
    
    Args:
        config (dict): Configuration data
    
    Returns:
        str: OpenAI embedding model name
    """
    return config.get("openaiEmbeddingModel", "text-embedding-3-small")

def get_google_embedding_model(config):
    """
    Get Google embedding model from configuration.
    
    Args:
        config (dict): Configuration data
    
    Returns:
        str: Google embedding model name
    """
    return config.get("googleEmbeddingModel", "text-embedding-005")

def get_sentence_transformer_model(config):
    """
    Get Sentence Transformer model from configuration.
    
    Args:
        config (dict): Configuration data
    
    Returns:
        str: Sentence Transformer model name
    """
    return config.get("sentenceTransformerModel", "multi-qa-mpnet-base-cos-v1")
