import os, requests
from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv('STACKEXCHANGE_KEY') or None
BASE = 'https://api.stackexchange.com/2.3'  # ← ADD THIS LINE!

def get_tag_info(tag: str, site: str='stackoverflow'):
    url = f'{BASE}/tags/{tag}/info'
    params = {'site': site}
    if KEY:
        params['key'] = KEY
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    items = j.get('items', [])
    if items:
        return {
            'tag': tag,
            'count': items[0].get('count'),
            'followers': items[0].get('followers'),
        }
    return None

def get_trending_tags(limit=5):
    """Get popular ML/AI Stack Overflow tags"""
    url = f'{BASE}/tags'
    params = {
        'pagesize': limit*2, 
        'sort': 'popular', 
        'order': 'desc',
        'site': 'stackoverflow'
    }
    if KEY:
        params['key'] = KEY
        
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    items = resp.json().get('items', [])
    
    # AI/ML tags priority
    ai_keywords = ['machine-learning', 'deep-learning', 'artificial-intelligence', 'nlp']
    ai_tags = [tag for tag in items if any(kw in tag['name'].lower() for kw in ai_keywords)]
    
    trending = []
    for tag in ai_tags[:limit] or items[:limit]:
        trending.append({
            'tool_name': tag['name'],
            'questions': tag.get('count', 0),
            'followers': tag.get('followers', 0),
            'url': f"https://stackoverflow.com/questions/tagged/{tag['name']}"
        })
    return trending
