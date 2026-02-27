# API Key Distribution Documentation

## Overview
This system uses 8 API keys distributed across 16 Moppie folders. Each API key is shared by exactly 2 folders.

## Distribution Map

| API Key Index | Moppie Folders | User IDs |
|---------------|----------------|----------|
| 0 | Moppie0, Moppie1 | 0, 1 |
| 1 | Moppie2, Moppie3 | 2, 3 |
| 2 | Moppie4, Moppie5 | 4, 5 |
| 3 | Moppie6, Moppie7 | 6, 7 |
| 4 | Moppie8, Moppie9 | 8, 9 |
| 5 | Moppie10, Moppie11 | 10, 11 |
| 6 | Moppie12, Moppie13 | 12, 13 |
| 7 | Moppie14, Moppie15 | 14, 15 |

## Files Modified

### Created Files:
- `central_config.py` - Central configuration file containing all API keys
- `update_configs.py` - Script to update all Moppie config files
- `API_KEY_DISTRIBUTION.md` - This documentation file

### Updated Files:
- All `MoppieX/scrapping/config.py` files (X = 0 to 15)

## How It Works

1. **Central Configuration**: All API keys are stored in `central_config.py`
2. **Dynamic Assignment**: Each Moppie folder's config.py imports from central_config and gets the appropriate API key based on its user_id
3. **Load Balancing**: API keys are distributed using the formula: `api_index = user_id // 2`

## Usage

Each Moppie folder now automatically gets the correct API key:

```python
# In any MoppieX/scrapping/config.py
from central_config import get_headers
headers = get_headers(user_id)  # Automatically gets the right API key
```

## Benefits

1. **Centralized Management**: All API keys in one place
2. **Easy Updates**: Change API keys in one file instead of 16
3. **Load Distribution**: Each API key handles exactly 2 folders
4. **No Duplication**: No need for separate virtual environments
5. **Scalable**: Easy to add more API keys or folders