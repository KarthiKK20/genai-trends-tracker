
import os, json
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DB')
}
def insert_metric_row(conn, row):
    sql = ("INSERT INTO metrics_raw (tool_name, platform, metric_name, metric_value, metric_text, retrieved_at, source_url, extra_json)"
           " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
    cur = conn.cursor()
    cur.execute(sql, (
        row.get('tool_name'), row.get('platform'), row.get('metric_name'), row.get('metric_value'),
        row.get('metric_text'), row.get('retrieved_at') or datetime.utcnow(), row.get('source_url'), json.dumps(row.get('extra_json') or {})
    ))
    conn.commit()
    cur.close()
