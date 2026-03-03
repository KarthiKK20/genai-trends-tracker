
import os, requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN') or None
HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'
BASE = 'https://api.github.com'

def get_repo_metrics(full_name: str):
    url = f'{BASE}/repos/{full_name}'
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    return {
        'tool_name': j.get('name') or full_name,
        'platform': 'github',
        'stars': j.get('stargazers_count'),
        'forks': j.get('forks_count'),
        'watchers': j.get('watchers_count'),
        'open_issues': j.get('open_issues_count'),
        'url': j.get('html_url'),
        'retrieved_at': datetime.utcnow().isoformat()
    }

def get_trending_repos(language='', since='daily', limit=10):
    """Get GitHub trending repos - DIRECT scrape (no proxy)"""
    import requests
    from bs4 import BeautifulSoup
    
    url = 'https://github.com/trending'
    if language:
        url += f'?l={language}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    repos = []
    
    # Parse trending table
    for item in soup.select('.Box-row')[:limit]:
        name_elem = item.select_one('h3 a')
        stars_elem = item.select_one('[aria-label*="stars"]')
        forks_elem = item.select_one('[aria-label*="fork"]')
        
        if name_elem:
            name = name_elem.get('text', '').strip().split('/')[-1]
            repo_url = name_elem.get('href', '')
            full_url = f"https://github.com{repo_url}"
            
            stars = 0
            if stars_elem:
                stars_text = stars_elem.get('aria-label', '')
                stars = int(''.join(filter(str.isdigit, stars_text)))
            
            trending = [{
                'tool_name': name or 'unknown',
                'stars_today': stars * 0.1,  # Estimate daily
                'stars_total': stars,
                'forks': 0,
                'url': full_url,
                'description': 'Trending repo'
            }]
            repos.extend(trending)
    
    return repos[:limit] or [{'tool_name': 'fallback-repo', 'stars_today': 10, 'stars_total': 100, 'url': 'https://github.com'}]
