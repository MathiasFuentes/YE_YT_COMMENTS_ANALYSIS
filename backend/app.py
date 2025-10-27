import os, sqlite3
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

# Cargar .env de la RAÍZ del repo, no del cwd actual
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent           # .../backend
ROOT_DIR = BASE_DIR.parent                           # .../YE_YT_COMMENTS_ANALYSIS
load_dotenv(ROOT_DIR / ".env")

app = Flask(__name__)
CORS(app)

# 1) Si viene de .env, úsalo; si no, construir ../data/databaser.db relativo al archivo
DB_PATH = os.getenv("DATABASE_URL") or str((ROOT_DIR / "data" / "databaser.db").resolve())

def get_db_connection():
    # Asegura que el directorio existe (por si usas relative en otro entorno)
    db_dir = Path(DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint de debug para verificar que apuntas a la BD correcta
@app.route("/_debug/db")
def debug_db():
    from os.path import getsize, abspath
    info = {
        "db_path": abspath(DB_PATH),
        "db_exists": Path(DB_PATH).exists(),
        "db_size_bytes": getsize(DB_PATH) if Path(DB_PATH).exists() else 0,
    }
    return info


@app.route("/kpis")
def get_kpis():
    from_date = request.args.get("from")
    to_date   = request.args.get("to")

    # Base: contar por etiqueta real (pos/neg/neu)
    query = """
        SELECT
            SUM(CASE WHEN s.sentiment_label = 'pos' THEN 1 ELSE 0 END) AS total_pos,
            SUM(CASE WHEN s.sentiment_label = 'neg' THEN 1 ELSE 0 END) AS total_neg,
            SUM(CASE WHEN s.sentiment_label = 'neu' THEN 1 ELSE 0 END) AS total_neu,
            COUNT(*) AS total_comments
        FROM scores s
    """

    params = []
    where = []

    # Solo si hay filtros de fecha, nos unimos a posts para filtrar por created_at
    if from_date or to_date:
        query += " JOIN posts p ON p.post_id = s.post_id"
        if from_date:
            where.append("DATE(p.created_at) >= ?")
            params.append(from_date)
        if to_date:
            where.append("DATE(p.created_at) <= ?")
            params.append(to_date)

    if where:
        query += " WHERE " + " AND ".join(where)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return jsonify(dict(zip([c[0] for c in cur.description], row)))

# --- /series sin cambios (usa posts.created_at + scores.sentiment_label) ---
@app.route("/series")
def get_series():
    from_date = request.args.get("from")
    to_date   = request.args.get("to")

    where = []
    params = []
    if from_date:
        where.append("DATE(p.created_at) >= ?")
        params.append(from_date)
    if to_date:
        where.append("DATE(p.created_at) <= ?")
        params.append(to_date)

    query = f"""
        SELECT 
            DATE(p.created_at) AS day,
            SUM(CASE WHEN s.sentiment_label = 'pos' THEN 1 ELSE 0 END) AS pos,
            SUM(CASE WHEN s.sentiment_label = 'neg' THEN 1 ELSE 0 END) AS neg,
            SUM(CASE WHEN s.sentiment_label = 'neu' THEN 1 ELSE 0 END) AS neu,
            COUNT(*) AS total
        FROM posts p
        JOIN scores s ON p.post_id = s.post_id
        {("WHERE " + " AND ".join(where)) if where else ""}
        GROUP BY day
        ORDER BY day;
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])




# ----------------------------------------------------
# 🗓️ Endpoint: eventos especiales (opcional)
# ----------------------------------------------------
@app.route("/events")
def get_events():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rowid as id,
               date as event_date,
               tag as title,
               description,
               source_url
        FROM events
        ORDER BY date
    """)
    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])
@app.route("/")
def index():
    return {
        "name": "YE_YT_COMMENTS_ANALYSIS API",
        "endpoints": ["/series", "/kpis", "/events"],
        "status": "ok"
    }

@app.route("/health")
def health():
    return {"status": "healthy"}

# ----------------------------------------------------
# 🚀 Ejecutar servidor
# ----------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
