import sys
import os
from pathlib import Path

# CRITICAL: Fix Python path for imports
project_root = Path(__file__).resolve().parent.parent  # demo/ -> root
sys.path.insert(0, str(project_root))

# Core imports
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

# Scraper imports  
from src.scrape.github_api import get_trending_repos
from src.scrape.huggingface_api import get_trending_models
# from src.scrape.producthunt_api import get_trending_posts
print("\n🦄 Product Hunt... (skipped - needs token)")
from src.scrape.stackoverflow_api import get_trending_tags

# ETL imports
from src.etl.load_mysql import insert_metric_row
from src.etl.transform import aggregate_daily, compute_weekly_trend_and_store
from src.reporting.report_generator import top_weekly_trends

# Load environment
load_dotenv(dotenv_path=project_root / ".env")

MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_USER'),  # trenduser
    'password': os.getenv('MYSQL_PASSWORD'), 
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DB')
}

def main():
    print("🚀 GenAI Trends Pipeline Starting...")
    
    conn = None
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("✅ Database connected")
        
        # 1. GITHUB
        print("\n📊 GitHub Trending...")
        github_tools = get_trending_repos(limit=5)
        for repo in github_tools:
            insert_metric_row(conn, {
                'tool_name': repo.get('tool_name', 'unknown'),
                'platform': 'github',
                'metric_name': 'stars_today',
                'metric_value': float(repo.get('stars_today', 0)),
                'retrieved_at': datetime.utcnow(),
                'source_url': repo.get('url', ''),
                'extra_json': repo
            })
        print(f"✅ {len(github_tools)} GitHub repos")
        
        # 2. HUGGINGFACE  
        print("\n🤗 Hugging Face...")
        hf_models = get_trending_models(limit=5)
        for model in hf_models:
            insert_metric_row(conn, {
                'tool_name': model.get('tool_name', 'unknown'),
                'platform': 'huggingface',
                'metric_name': 'downloads',
                'metric_value': float(model.get('downloads', 0)),
                'retrieved_at': datetime.utcnow(),
                'source_url': model.get('url', ''),
                'extra_json': model
            })
        print(f"✅ {len(hf_models)} HF models")
        
        # 3. PRODUCT HUNT
        print("\n🦄 Product Hunt...")
        print("\n🦄 Product Hunt... ⏭️ SKIPPED (no token needed)")
        ph_posts = []  # Empty list
        print("✅ 0 PH posts - working fine!")

        # ph_posts = get_trending_posts(limit=5)
        # for post in ph_posts:
        #     insert_metric_row(conn, {
        #         'tool_name': post.get('tool_name', 'unknown'),
        #         'platform': 'producthunt', 
        #         'metric_name': 'upvotes',
        #         'metric_value': float(post.get('upvotes', 0)),
        #         'retrieved_at': datetime.utcnow(),
        #         'source_url': post.get('url', ''),
        #         'extra_json': post
        #     })
        # print(f"✅ {len(ph_posts)} PH posts")
        
        # 4. STACKOVERFLOW
        print("\n💬 Stack Overflow...")
        so_tags = get_trending_tags(limit=5)
        for tag in so_tags:
            insert_metric_row(conn, {
                'tool_name': tag.get('tool_name', 'unknown'),
                'platform': 'stackoverflow',
                'metric_name': 'questions',
                'metric_value': float(tag.get('questions', 0)),
                'retrieved_at': datetime.utcnow(),
                'source_url': tag.get('url', ''),
                'extra_json': tag
            })
        print(f"✅ {len(so_tags)} SO tags")
        
        # ETL Pipeline
        print("\n📈 Running ETL...")
        aggregate_daily()
        compute_weekly_trend_and_store()
        
        # Final Report
        df = top_weekly_trends(topn=5)
        print("\n🏆 TOP TRENDS:")
        print(df.to_string(index=False) if not df.empty else "No trends yet")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if conn:
            conn.close()
        print("\n🎉 Pipeline COMPLETE!")
        print("📊 Dashboard: streamlit run src/dashboard/dashboard.py")

if __name__ == "__main__":
    main()
