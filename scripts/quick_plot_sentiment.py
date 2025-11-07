# quick_plot_sentiment.py
# Uso:
#   python quick_plot_sentiment.py
# Opcional: variables de entorno para personalizar
#   set DB_PATH=C:\ruta\analysis.db
#   set SOURCE=all          # youtube | reddit | all
#   set FROM_DATE=2020-01-01
#   set TO_DATE=2022-12-31

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
DB_PATH = os.getenv("DATABASE_URL", "./data/databaser.db")
SOURCE    = os.environ.get("SOURCE", "all")           # 'youtube' | 'reddit' | 'all'
FROM_DATE = os.environ.get("FROM_DATE", "2020-01-01")
TO_DATE   = os.environ.get("TO_DATE",   "2022-12-31")

def table_exists(conn, name: str) -> bool:
    q = "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?"
    return conn.execute(q, (name,)).fetchone() is not None

def load_from_aggregates(conn):
    base = """
        SELECT bucket_date AS date, pos, neu, neg, total_posts, total_interactions, source
        FROM aggregates
        WHERE granularity='day'
          AND date(bucket_date) BETWEEN date(?) AND date(?)
    """
    args = (FROM_DATE, TO_DATE)
    if SOURCE != "all":
        base += " AND source=?"
        args += (SOURCE,)
    base += " ORDER BY bucket_date ASC"
    df = pd.read_sql_query(base, conn, params=args, parse_dates=["date"])
    return df

def compute_on_the_fly(conn):
    # Agregado diario desde posts + scores (por si no existe 'aggregates')
    where_src = "" if SOURCE == "all" else "AND p.source = ?"
    args = (FROM_DATE, TO_DATE) if SOURCE == "all" else (FROM_DATE, TO_DATE, SOURCE)
    q = f"""
        SELECT
            date(p.created_at) AS date,
            p.source AS source,
            SUM(CASE WHEN s.sentiment_label='pos' THEN 1 ELSE 0 END) AS pos,
            SUM(CASE WHEN s.sentiment_label='neu' THEN 1 ELSE 0 END) AS neu,
            SUM(CASE WHEN s.sentiment_label='neg' THEN 1 ELSE 0 END) AS neg,
            COUNT(*) AS total_posts,
            SUM(COALESCE(p.like_count,0)+COALESCE(p.reply_count,0)+COALESCE(p.score,0)) AS total_interactions
        FROM posts p
        JOIN scores s ON s.post_id = p.post_id
        WHERE date(p.created_at) BETWEEN date(?) AND date(?)
        {where_src}
        GROUP BY date, p.source
        ORDER BY date ASC
    """
    df = pd.read_sql_query(q, conn, params=args, parse_dates=["date"])
    return df

def main():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"No se encontró la base: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        if table_exists(conn, "aggregates"):
            df = load_from_aggregates(conn)
        else:
            df = compute_on_the_fly(conn)

    if df.empty:
        raise SystemExit("No hay datos para el rango/criterio elegido. Revisa SOURCE/fechas.")

    # Si pediste 'all', agregamos (sumamos) por fecha para un gráfico único
    if SOURCE == "all":
        df_plot = df.groupby("date", as_index=False)[["pos","neu","neg","total_posts","total_interactions"]].sum()
    else:
        df_plot = df.copy()

    # --- Gráfico 1: Serie temporal apilada (pos/neu/neg)
    fig1 = plt.figure(figsize=(11, 5))
    df_plot = df_plot.sort_values("date")
    x = df_plot["date"]
    y_pos = df_plot["pos"].fillna(0).astype(int)
    y_neu = df_plot["neu"].fillna(0).astype(int)
    y_neg = df_plot["neg"].fillna(0).astype(int)

    # apilado simple
    plt.stackplot(x, y_pos, y_neu, y_neg, labels=["Positivo", "Neutro", "Negativo"])
    plt.legend(loc="upper left")
    title_src = SOURCE if SOURCE != "all" else "todas las fuentes"
    plt.title(f"Evolución del sentimiento por día ({title_src})")
    plt.xlabel("Fecha")
    plt.ylabel("Conteo de publicaciones/comentarios")
    plt.tight_layout()

    # --- Gráfico 2: Distribución total (barras)
    fig2 = plt.figure(figsize=(7, 4))
    totals = {
        "Positivo": int(y_pos.sum()),
        "Neutro":   int(y_neu.sum()),
        "Negativo": int(y_neg.sum()),
    }
    plt.bar(list(totals.keys()), list(totals.values()))
    plt.title(f"Distribución total de etiquetas ({title_src})")
    plt.xlabel("Etiqueta")
    plt.ylabel("Conteo")
    plt.tight_layout()

    plt.show()

if __name__ == "__main__":
    main()
