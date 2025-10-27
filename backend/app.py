from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os

DB_PATH = os.environ.get("DATABASE_URL", os.path.join("..", "data", "analysis.db"))
app = Flask(__name__)
CORS(app)

def q(sql, params=()):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

@app.get("/series")
def series():
    f = request.args.get("from", "2020-01-01")
    t = request.args.get("to",   "2022-12-31")
    sql = """
    SELECT bucket_date AS date, pos, neu, neg, total_posts, total_interactions
    FROM aggregates
    WHERE source='youtube' AND granularity='day'
      AND date(bucket_date) BETWEEN date(?) AND date(?)
    ORDER BY bucket_date ASC
    """
    return jsonify(q(sql, (f, t)))

@app.get("/kpis")
def kpis():
    f = request.args.get("from", "2020-01-01")
    t = request.args.get("to",   "2022-12-31")
    sql = """
    SELECT SUM(pos) pos, SUM(neu) neu, SUM(neg) neg, SUM(total_posts) total
    FROM aggregates
    WHERE source='youtube' AND granularity='day'
      AND date(bucket_date) BETWEEN date(?) AND date(?)
    """
    rows = q(sql, (f, t))
    return jsonify(rows[0] if rows else {"pos":0,"neu":0,"neg":0,"total":0})

@app.get("/events")
def events():
    f = request.args.get("from", "2020-01-01")
    t = request.args.get("to",   "2022-12-31")
    sql = """
    SELECT date, tag, description, source_url
    FROM events
    WHERE date(date) BETWEEN date(?) AND date(?)
    ORDER BY date ASC
    """
    return jsonify(q(sql, (f, t)))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("FLASK_RUN_PORT", "5000")), debug=True)
