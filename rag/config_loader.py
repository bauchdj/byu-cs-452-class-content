import json
import os

def load_config(config_path="config.json"):
    """
    Load configuration from config.json file.
    
    To set up your configuration:
    1. Copy config_template.json to config.json
    2. Fill in your API keys and project IDs
    3. For Google Cloud, ensure you have set up Application Default Credentials (ADC)
       - Install Google Cloud CLI and run: gcloud auth application-default login
       - Or set GOOGLE_APPLICATION_CREDENTIALS environment variable
    
    Args:
        config_path (str): Path to the configuration file
    
    Returns:
        dict: Configuration data
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found. Please create it first.\n\nTo set up your configuration:\n1. Copy config_template.json to config.json\n2. Fill in your API keys and project IDs\n3. For Google Cloud, ensure you have set up Application Default Credentials (ADC)\n   - Install Google Cloud CLI and run: gcloud auth application-default login\n   - Or set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    
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

def get_google_ai_key(config):
    """
    Get Google AI API key from configuration.
    
    Args:
        config (dict): Configuration data
    
    Returns:
        str: Google AI API key
    """
    google_ai_key = config.get("googleAiKey")
    if not google_ai_key or google_ai_key == "insert your Google AI API key here":
        raise ValueError("Google AI API key not found in config.json. Please add your API key as 'googleAiKey'.")
    return google_ai_key
