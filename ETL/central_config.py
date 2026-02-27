import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Central API Configuration
# 8 API keys for 16 Moppie folders (each API key used by 2 folders)
# API keys are loaded from .env file for security

API_KEYS = [
    os.getenv("API_KEY_0"),
    os.getenv("API_KEY_1"),
    os.getenv("API_KEY_2"),
    os.getenv("API_KEY_3"),
    os.getenv("API_KEY_4"),
    os.getenv("API_KEY_5"),
    os.getenv("API_KEY_6"),
    os.getenv("API_KEY_7"),
]

def get_api_key(user_id):
    """
    Get API key for a specific user_id.
    Each API key is used by 2 users (user_id // 2)
    """
    api_index = user_id // 2
    if api_index >= len(API_KEYS):
        raise ValueError(f"Invalid user_id: {user_id}. Maximum user_id is {len(API_KEYS) * 2 - 1}")
    return API_KEYS[api_index]

def get_headers(user_id):
    """
    Get headers with the appropriate API key for a specific user_id
    """
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {get_api_key(user_id)}"
    }

# Distribution configuration
DISTRIBUTION_CONFIG = {
    'user_count': 16,
    'api_count': 8
}