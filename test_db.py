import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()
config = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DB')
}

try:
    conn = mysql.connector.connect(**config)
    print("✅ MySQL Connected! Tables ready.")
    conn.close()
except Exception as e:
    print(f"❌ DB Error: {e}")
