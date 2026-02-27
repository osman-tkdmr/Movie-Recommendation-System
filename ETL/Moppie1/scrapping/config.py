# API configuration - Updated to use central config
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from central_config import get_headers

# Get headers from central config based on user_id
headers = get_headers(3)

distibution = {
    'user_count': 16,
    'user_id': 3
}
