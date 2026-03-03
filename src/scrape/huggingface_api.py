
import os, requests
from dotenv import load_dotenv
load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN') or None
HEADERS = {'Accept': 'application/json'}
if HF_TOKEN:
    HEADERS['Authorization'] = f'Bearer {HF_TOKEN}'
BASE = 'https://huggingface.co/api'

def get_model_info(model_id: str):
    url = f'{BASE}/models/{model_id}'
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    return {
        'model_id': model_id,
        'likes': j.get('likes'),
        'downloads': j.get('downloads', 0),
        'lastModified': j.get('lastModified'),
        'url': f'https://huggingface.co/{model_id}'
    }

def get_trending_models(limit=10):
    """Get trending HF models"""
    url = 'https://huggingface.co/api/models'
    params = {'sort': 'downloads', 'limit': limit}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    models = resp.json()
    trending = []
    for model in models:
        trending.append({
            'tool_name': model['id'],
            'downloads': model.get('downloads', 0),
            'likes': model.get('likes', 0),
            'url': f"https://huggingface.co/{model['id']}",
            'lastModified': model.get('lastModified', '')
        })
    return trending
