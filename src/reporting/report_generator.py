
import mysql.connector, os, pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DB')
}
def top_weekly_trends(week_start=None, topn=5):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor(dictionary=True)
    if week_start is None:
        week_start = (datetime.utcnow() - timedelta(days=7)).date()
    q = "SELECT t.canonical_name as tool_name, ts.trend_score, ts.rank, ts.components FROM trend_scores ts JOIN tools t ON ts.tool_id = t.tool_id WHERE ts.score_date = %s ORDER BY ts.trend_score DESC LIMIT %s"
    cur.execute(q, (week_start, topn))
    rows = cur.fetchall()
    df = pd.DataFrame(rows)
    out_csv = f'./data/reports/top_trends_{week_start}.csv'
    os.makedirs('./data/reports', exist_ok=True)
    df.to_csv(out_csv, index=False)
    cur.close(); conn.close()
    print('Wrote', out_csv)
    return df
