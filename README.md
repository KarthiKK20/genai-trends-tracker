
GenAI Trend Tracker 
======================================
This package tracks GenAI/ML tools across GitHub, Product Hunt, Hugging Face, and Stack Overflow.
Reddit integration has been removed due to inaccessible API.

Run steps (Linux, Python 3.10+):
1. pip install -r requirements.txt
2. cp .env.example .env   # edit MySQL creds (and optional API tokens)
3. mysql -u root -p < db/schema.sql
4. python3 -m src.demo.run_demo
