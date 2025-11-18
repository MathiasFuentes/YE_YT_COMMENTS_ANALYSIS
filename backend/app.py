import sqlite3
import pandas as pd
import ast
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- Configuración ---
DB_PATH = '../data/databaser.db'
AGGREGATES_TABLE = 'aggregates'
EVENTS_TABLE = 'events'
TABLA_TEMAS = 'datos_finales_con_temas'

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Crea una conexión a la base de datos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Cambiamos a None para que Pandas lea la DB
        conn.row_factory = None 
        return conn
    except Exception as e:
        print(f"Error al conectar a DB: {e}")
        return None


@app.route('/topics')
def get_topics():
    # ... (el resto de tu función /topics sin cambios) ...
    # Asegurémonos de que la conexión vuelva a usar sqlite3.Row
    # para que el resto de los endpoints funcionen.
    conn = get_db_connection()
    if conn: conn.row_factory = sqlite3.Row
    else: return jsonify({"error": "Datos no disponibles"}), 500
    
    from_date = request.args.get('from', '2020-10-24')
    to_date = request.args.get('to', '2025-10-23')

    query = f"""
        SELECT 
            t.sentiment_label, t.tematicas
        FROM {TABLA_TEMAS} AS t
        INNER JOIN posts AS p ON t.post_id = p.post_id
        WHERE date(p.created_at) BETWEEN ? AND ?
    """
    
    try:
        df_datos_finales = pd.read_sql_query(query, conn, params=(from_date, to_date))
        conn.close()
    except Exception as e:
        print(f"Error al leer la tabla {TABLA_TEMAS}: {e}")
        return jsonify({"error": "Datos no disponibles"}), 500

    if df_datos_finales.empty:
        return jsonify({"error": "La tabla de temas está vacía"}), 500

    df_datos_finales['tematicas'] = df_datos_finales['tematicas'].apply(ast.literal_eval)
    df_explotado = df_datos_finales.explode('tematicas')
    df_agrupado = df_explotado.groupby(['tematicas', 'sentiment_label']).size()
    
    resultado_json = {}
    for (tema, sentimiento), count in df_agrupado.items():
        if not tema:
            continue
        if tema not in resultado_json:
            resultado_json[tema] = {"pos": 0, "neg": 0, "neu": 0}
        
        if sentimiento == 'pos':
            resultado_json[tema]['pos'] = int(count)
        elif sentimiento == 'neg':
            resultado_json[tema]['neg'] = int(count)
        elif sentimiento == 'neu':
            resultado_json[tema]['neu'] = int(count)
            
    return jsonify(resultado_json)


@app.route('/kpis')
def get_kpis():
    # ... (tu endpoint /kpis sin cambios) ...
    conn = get_db_connection()
    if conn: conn.row_factory = sqlite3.Row
    else: return jsonify({"error": "Datos no disponibles"}), 500

    from_date = request.args.get('from', '2020-10-24')
    to_date = request.args.get('to', '2025-10-23')
    
    query = f"""
        SELECT 
            SUM(pos) as total_pos, 
            SUM(neg) as total_neg, 
            SUM(neu) as total_neu, 
            SUM(total_posts) as total_comments
        FROM {AGGREGATES_TABLE}
        WHERE bucket_date BETWEEN ? AND ?
    """
    
    try:
        cursor = conn.cursor()
        row = cursor.execute(query, (from_date, to_date)).fetchone()
        conn.close()
        
        return jsonify(dict(row) if row else {})
        
    except Exception as e:
        print(f"Error en /kpis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/series')
def get_series():
    # ... (tu endpoint /series sin cambios) ...
    conn = get_db_connection()
    if conn: conn.row_factory = sqlite3.Row
    else: return jsonify({"error": "Datos no disponibles"}), 500

    from_date = request.args.get('from', '2020-10-24')
    to_date = request.args.get('to', '2025-10-23')

    query = f"""
        SELECT 
            bucket_date AS day, 
            pos, 
            neg, 
            neu, 
            total_posts AS total
        FROM {AGGREGATES_TABLE}
        WHERE granularity = 'day' 
          AND bucket_date BETWEEN ? AND ?
        ORDER BY bucket_date
    """
    
    try:
        cursor = conn.cursor()
        rows = cursor.execute(query, (from_date, to_date)).fetchall()
        conn.close()
        
        data = [dict(row) for row in rows]
        return jsonify(data)
        
    except Exception as e:
        print(f"Error en /series: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/events')
def get_events():
    # ... (tu endpoint /events sin cambios) ...
    conn = get_db_connection()
    if conn: conn.row_factory = sqlite3.Row
    else: return jsonify({"error": "Datos no disponibles"}), 500

    query = f"""
        SELECT 
            date AS event_date, 
            description AS title, 
            tag
        FROM {EVENTS_TABLE}
    """
    
    try:
        cursor = conn.cursor()
        rows = cursor.execute(query).fetchall()
        conn.close()
        
        data = [dict(row) for row in rows]
        return jsonify(data)
        
    except Exception as e:
        print(f"Error en /events: {e}")
        return jsonify({"error": str(e)}), 500

# --- ¡NUEVO ENDPOINT AÑADIDO AQUÍ! ---
@app.route('/series/engagement_by_sentiment')
def get_engagement_by_sentiment():
    """
    Calcula el promedio de likes y respuestas por sentimiento.
    Usa los filtros de fecha 'from' y 'to'.
    """
    # 1. Conexión a la DB (siguiendo tu patrón de /kpis, /series, etc.)
    conn = get_db_connection()
    if conn:
        conn.row_factory = sqlite3.Row
    else:
        return jsonify({"error": "Datos no disponibles"}), 500

    # 2. Obtener parámetros de fecha (igual que en tus otros endpoints)
    from_date = request.args.get('from', '2020-10-24')
    to_date = request.args.get('to', '2025-10-23')

    # 3. Consulta SQL
    #    Usa 'p.created_at' (visto en tu endpoint /topics) para las fechas.
    sql = """
        SELECT
            s.sentiment_label,
            AVG(p.like_count)  AS avg_likes,
            AVG(p.reply_count) AS avg_replies
        FROM scores AS s
        JOIN posts  AS p ON s.post_id = p.post_id
        WHERE p.source = 'youtube'
        AND date(p.created_at) BETWEEN ? AND ?  -- Filtro de fecha
        GROUP BY s.sentiment_label
        ORDER BY s.sentiment_label;
    """
    
    try:
        # 4. Ejecutar y formatear (igual que en tu endpoint /series)
        cursor = conn.cursor()
        rows = cursor.execute(sql, (from_date, to_date)).fetchall()
        conn.close()
        
        # 5. Formatear la salida para el JSON que espera el frontend
        data = []
        for row in rows:
            data.append({
                "sentiment_label": row["sentiment_label"],
                # Redondear y manejar nulos (si AVG devuelve None)
                "avg_likes": round(row["avg_likes"] or 0, 2),
                "avg_replies": round(row["avg_replies"] or 0, 2)
            })
        
        return jsonify(data)
        
    except Exception as e:
        # 6. Manejo de errores (igual que en tus otros endpoints)
        print(f"Error en /series/engagement_by_sentiment: {e}")
        return jsonify({"error": str(e)}), 500
# ------------------------------------

# (Asegúrate de que 'AGGREGATES_TABLE' esté definida arriba en tu archivo)

@app.route('/sentiment_timeline')
def get_sentiment_timeline():
    """
    Serie de sentimiento normalizado (%), agregada por semestre.
    Usa la tabla 'aggregates' como fuente diaria y agrupa en pandas.
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datos no disponibles"}), 500

    from_date = request.args.get('from', '2020-10-24')
    to_date   = request.args.get('to',   '2025-10-23')

    # Traemos datos DIARIOS desde aggregates
    query = f"""
        SELECT
            bucket_date AS date,
            pos,
            neu,
            neg,
            total_posts AS total
        FROM {AGGREGATES_TABLE}
        WHERE granularity = 'day'
          AND bucket_date BETWEEN ? AND ?
          AND total_posts > 0
        ORDER BY bucket_date
    """

    try:
        df = pd.read_sql_query(query, conn, params=(from_date, to_date))
        conn.close()

        if df.empty:
            return jsonify([])

        # Aseguramos que 'date' sea datetime
        df['date'] = pd.to_datetime(df['date'])

        # Año y semestre (1 = ene–jun, 2 = jul–dic)
        df['year'] = df['date'].dt.year
        df['semester'] = df['date'].dt.month.apply(lambda m: 1 if m <= 6 else 2)

        # Agrupamos por año + semestre (sumando volúmenes)
        agg = (
            df.groupby(['year', 'semester'], as_index=False)
              .agg({'pos': 'sum', 'neu': 'sum', 'neg': 'sum', 'total': 'sum'})
        )

        # Para Chart.js seguimos usando un campo 'date':
        # ponemos una fecha representativa del semestre
        # S1 -> YYYY-01-01, S2 -> YYYY-07-01
        agg['date'] = agg.apply(
            lambda r: f"{int(r['year'])}-01-01" if r['semester'] == 1
                      else f"{int(r['year'])}-07-01",
            axis=1
        )

        # Porcentajes
        agg['pos_percent'] = (agg['pos'] / agg['total'] * 100).round(2)
        agg['neg_percent'] = (agg['neg'] / agg['total'] * 100).round(2)
        agg['neu_percent'] = (agg['neu'] / agg['total'] * 100).round(2)

        # Solo las columnas que necesita el frontend
        result = agg[['date', 'pos_percent', 'neg_percent', 'neu_percent']].to_dict(orient='records')
        return jsonify(result)

    except Exception as e:
        print(f"Error en /sentiment_timeline: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/top_comments')
def get_top_comments():
    """
    Devuelve los comentarios históricos con más likes.
    Opcionalmente se puede filtrar por rango de fechas usando ?from=YYYY-MM-DD&to=YYYY-MM-DD.
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Datos no disponibles"}), 500

    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    from_date = request.args.get('from')
    to_date   = request.args.get('to')
    limit     = request.args.get('limit', 8)

    try:
        limit = int(limit)
        if limit <= 0 or limit > 50:
            limit = 8
    except ValueError:
        limit = 8

    sql = """
        SELECT
            p.post_id,
            p.author,
            p.text,
            p.like_count,
            p.created_at,
            p.url,
            s.sentiment_label
        FROM posts AS p
        LEFT JOIN scores AS s ON s.post_id = p.post_id
        WHERE p.source = 'youtube'
    """

    params = []
    if from_date and to_date:
        sql += " AND date(p.created_at) BETWEEN ? AND ?"
        params.extend([from_date, to_date])

    sql += " ORDER BY p.like_count DESC LIMIT ?"
    params.append(limit)

    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error en /top_comments: {e}")
        return jsonify({"error": "Datos no disponibles"}), 500

    data = []
    for row in rows:
        data.append({
            "post_id": row["post_id"],
            "author": row["author"],
            "text": row["text"],
            "like_count": row["like_count"],
            "created_at": row["created_at"],
            "url": row["url"],
            "sentiment_label": row["sentiment_label"],
        })

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)