# import os, requests, json
# from datetime import datetime
# from dotenv import load_dotenv
# load_dotenv()

# PH_TOKEN = os.getenv('PRODUCTHUNT_TOKEN') or None
# HEADERS = {'Accept': 'application/json'}
# if PH_TOKEN:
#     HEADERS['Authorization'] = f'Bearer {PH_TOKEN}'

# def get_trending_posts(limit=10):
#     """Get top Product Hunt AI/ML posts (no token needed for basic)"""
#     try:
#         # Use public RSS/JSON proxy for trending
#         url = 'https://api.producthunt.com/v2/posts/recent'
#         resp = requests.get(url, headers=HEADERS, timeout=15)
#         if resp.status_code == 401:  # No token
#             # Fallback to public scraping proxy
#             url = 'https://api.producthunt.achilles.me/v1/posts?days_ago=0&order=ORDER_VOTES'
#             resp = requests.get(url, timeout=15)
        
#         resp.raise_for_status()
#         data = resp.json()
        
#         posts = data.get('data', []) or data.get('posts', [])
#         trending = []
#         for post in posts[:limit]:
#             trending.append({
#                 'tool_name': post.get('name') or post.get('headline', ''),
#                 'upvotes': post.get('votes_count') or post.get('votesCount', 0),
#                 'url': post.get('discussion_url') or post.get('url'),
#                 'tagline': post.get('tagline', '')
#             })
#         return [p for p in trending if any(kw in p['tagline'].lower() 
#                    for kw in ['ai', 'ml', 'genai'])] or trending[:limit]
#     except Exception as e:
#         print(f"Product Hunt error: {e}")
#         return []
# Skip ProductHunt (needs token)
print("\n🦄 Product Hunt... (skipped - needs token)")
print("✅ 0 PH posts (add PRODUCTHUNT_TOKEN to .env)")
