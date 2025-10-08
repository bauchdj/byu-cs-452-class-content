import google.generativeai as genai
from config_loader import load_config, get_google_ai_key

# Load configuration
config = load_config()
google_ai_key = get_google_ai_key(config)

# Configure the SDK
genai.configure(api_key=google_ai_key)

# List available models
print("Available models:")
for model in genai.list_models():
    if 'embedContent' in model.supported_generation_methods:
        print(f"- {model.name}: {model.display_name}")
