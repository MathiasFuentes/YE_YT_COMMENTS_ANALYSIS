import sqlite3
import pandas as pd
import ast
from flask import Flask, jsonify, request
from flask_cors import CORS  # <-- 1. IMPORTA LA LIBRERÍA

# --- Configuración ---
DB_PATH = '../data/databaser.db'
AGGREGATES_TABLE = 'aggregates'
EVENTS_TABLE = 'events'
TABLA_TEMAS = 'datos_finales_con_temas'

app = Flask(__name__)
CORS(app)  # <-- 2. INICIALIZA CORS EN TU APP

def get_db_connection():
    """Crea una conexión a la base de datos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error al conectar a DB: {e}")
        return None

# --- ENDPOINT PARA EL NUEVO GRÁFICO DE TEMÁTICAS ---
@app.route('/topics')
def get_topics():
    query = f"SELECT sentiment_label, tematicas FROM {TABLA_TEMAS}"
    
    try:
        conn = get_db_connection()
        df_datos_finales = pd.read_sql_query(query, conn)
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
        
        # Corregido para usar las etiquetas 'pos', 'neg', 'neu'
        if sentimiento == 'pos':
            resultado_json[tema]['pos'] = int(count)
        elif sentimiento == 'neg':
            resultado_json[tema]['neg'] = int(count)
        elif sentimiento == 'neu':
            resultado_json[tema]['neu'] = int(count)
            
    return jsonify(resultado_json)

# --- Endpoints Originales (Mejorados) ---

@app.route('/kpis')
def get_kpis():
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
        conn = get_db_connection()
        cursor = conn.cursor()
        row = cursor.execute(query, (from_date, to_date)).fetchone()
        conn.close()
        
        return jsonify(dict(row) if row else {})
        
    except Exception as e:
        print(f"Error en /kpis: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/series')
def get_series():
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
        conn = get_db_connection()
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
    query = f"""
        SELECT 
            date AS event_date, 
            description AS title, 
            tag
        FROM {EVENTS_TABLE}
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        rows = cursor.execute(query).fetchall()
        conn.close()
        
        data = [dict(row) for row in rows]
        return jsonify(data)
        
    except Exception as e:
        print(f"Error en /events: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)