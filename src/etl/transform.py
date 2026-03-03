
import os, mysql.connector, pandas as pd, json
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
def aggregate_daily(date=None):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor(dictionary=True)
    if date is None:
        date = datetime.utcnow().date()
    start = datetime.combine(date, datetime.min.time())
    end = start + timedelta(days=1)
    query = "SELECT tool_name, platform, metric_name, AVG(metric_value) as metric_value FROM metrics_raw WHERE retrieved_at >= %s AND retrieved_at < %s GROUP BY tool_name, platform, metric_name"
    cur.execute(query, (start, end))
    rows = cur.fetchall()
    df = pd.DataFrame(rows)
    for _, r in df.iterrows():
        tcur = conn.cursor()
        tcur.execute("SELECT tool_id FROM tools WHERE canonical_name=%s", (r['tool_name'],))
        t = tcur.fetchone()
        if not t:
            tcur.execute("INSERT INTO tools (canonical_name, first_seen, last_seen) VALUES (%s, %s, %s)", (r['tool_name'], datetime.utcnow(), datetime.utcnow()))
            conn.commit()
            tool_id = tcur.lastrowid
        else:
            tool_id = t[0]
            tcur.execute("UPDATE tools SET last_seen=%s WHERE tool_id=%s", (datetime.utcnow(), tool_id))
            conn.commit()
        ival = r['metric_value'] if r['metric_value'] is not None else 0
        cur_ins = conn.cursor()
        cur_ins.execute("INSERT INTO metrics_daily (tool_id, platform, metric_name, metric_value, metric_date) VALUES (%s,%s,%s,%s,%s)",
                        (tool_id, r['platform'], r['metric_name'], float(ival), date))
        conn.commit()
    cur.close(); conn.close()
    print('Aggregated and inserted daily metrics for', date)
def compute_weekly_trend_and_store(week_start=None):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor(dictionary=True)
    if week_start is None:
        week_start = (datetime.utcnow() - timedelta(days=7)).date()
    q = "SELECT t.canonical_name as tool_name, md.platform, md.metric_name, SUM(md.metric_value) as metric_value FROM metrics_daily md JOIN tools t ON md.tool_id=t.tool_id WHERE md.metric_date >= %s GROUP BY t.canonical_name, md.platform, md.metric_name"
    cur.execute(q, (week_start,))
    rows = cur.fetchall()
    df = pd.DataFrame(rows)
    ag = {}
    for _, r in df.iterrows():
        ag.setdefault(r['tool_name'], {}).setdefault(r['platform'], {})[r['metric_name']] = r['metric_value']
    metrics = {}
    for tool, platforms in ag.items():
        for plat, m in platforms.items():
            for mn, val in m.items():
                metrics.setdefault(mn, []).append(val)
    norm = {}
    for mn, vals in metrics.items():
        mn_min = min(vals) if vals else 0
        mn_max = max(vals) if vals else 1
        norm[mn] = (mn_min, mn_max)
    PLATFORM_WEIGHTS = {
        'github': {'stars': 0.5, 'forks':0.2, 'watchers':0.1},
        'producthunt': {'upvotes':0.8},
        'huggingface': {'likes':0.6,'downloads':0.4},
        'stackoverflow': {'questions':0.7}
    }
    scores = []
    for tool, platforms in ag.items():
        total_score = 0.0
        components = {}
        for plat, m in platforms.items():
            for mn, val in m.items():
                mn_min, mn_max = norm.get(mn, (0,1))
                if mn_max - mn_min == 0:
                    nv = 0.0
                else:
                    nv = (val - mn_min) / (mn_max - mn_min)
                w = PLATFORM_WEIGHTS.get(plat, {}).get(mn, 0.1)
                comp = w * nv
                components[f"{plat}.{mn}"] = comp
                total_score += comp
        scores.append((tool, total_score, json.dumps(components)))
    scores.sort(key=lambda x: x[1], reverse=True)
    for rank, (tool, score, comps) in enumerate(scores, start=1):
        cur2 = conn.cursor()
        cur2.execute("SELECT tool_id FROM tools WHERE canonical_name=%s", (tool,))
        t = cur2.fetchone()
        if t:
            tool_id = t[0]
        else:
            cur2.execute("INSERT INTO tools (canonical_name, first_seen, last_seen) VALUES (%s,%s,%s)", (tool, datetime.utcnow(), datetime.utcnow()))
            conn.commit()
            tool_id = cur2.lastrowid
        cur2.execute("INSERT INTO trend_scores (tool_id, score_date, trend_score, `rank`, components) VALUES (%s,%s,%s,%s,%s)",
                     (tool_id, week_start, float(score), rank, comps))
        conn.commit()
    cur.close(); conn.close()
    print('Computed and stored weekly trend scores for week starting', week_start)
