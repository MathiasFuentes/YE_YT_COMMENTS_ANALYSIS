import os, re, sqlite3, sys, time
from contextlib import closing
from tqdm import tqdm

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline

DB_PATH = os.getenv("DATABASE_URL", "./data/databaser.db")
# DB_PATH = r"C:\Users\matia\Desktop\analysis.db\databaser.db"  # <-- AJUSTA RUTA SI ES NECESARIO
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
PIPE_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"  # lo guardaremos así en 'scores.model_name'

# ---------- helpers ----------
def clean_text(s: str) -> str:
    if s is None:
        return ""
    s = re.sub(r"http\S+", " ", s)            # URLs fuera
    s = re.sub(r"@\w+", "@user", s)           # menciones
    s = re.sub(r"#(\w+)", r"\1", s)           # hashtags -> palabra
    s = re.sub(r"\s+", " ", s).strip()
    return s

def get_device():
    if torch.cuda.is_available():
        return 0
    return -1  # CPU

# ---------- load model ----------
device = get_device()
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
clf = TextClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    device=device,               # 0 = GPU, -1 = CPU
    truncation=True,
    max_length=256,              # 256 tokens suele ser suficiente para comentarios
    batch_size=32                # ajusta a 16/64 según RAM/GPU
)

# El modelo devuelve labels tipo: "negative", "neutral", "positive"
def norm_label(lbl: str) -> str:
    l = lbl.lower()
    if l.startswith("pos"): return "pos"
    if l.startswith("neg"): return "neg"
    return "neu"

# ---------- main loop ----------
BATCH_SELECT = 2000   # cuántos recuperar de la BD por tanda
COMMIT_EVERY = 500    # cada cuántos inserts hacer commit

with closing(sqlite3.connect(DB_PATH)) as conn:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    cur = conn.cursor()

    # Cuenta cuántos posts NO tienen score con este modelo
    cur.execute("""
      SELECT COUNT(*)
      FROM posts p
      LEFT JOIN scores s ON s.post_id = p.post_id AND s.model_name = ?
      WHERE s.post_id IS NULL AND p.text IS NOT NULL AND length(p.text) > 0
    """, (PIPE_MODEL_NAME,))
    total_pending = cur.fetchone()[0]
    if total_pending == 0:
        print("No hay posts pendientes para este modelo. ¡Listo!")
        sys.exit(0)

    print(f"Pendientes por clasificar: {total_pending:,}")

    # Procesa por tandas para no cargar todo en memoria
    processed = 0
    inserted_since_commit = 0

    pbar = tqdm(total=total_pending, unit="post")
    while True:
        # Selecciona una tanda de posts aún no clasificados por este modelo
        cur.execute("""
          SELECT p.post_id, p.text
          FROM posts p
          LEFT JOIN scores s ON s.post_id = p.post_id AND s.model_name = ?
          WHERE s.post_id IS NULL AND p.text IS NOT NULL AND length(p.text) > 0
          ORDER BY p.created_at ASC
          LIMIT ?
        """, (PIPE_MODEL_NAME, BATCH_SELECT))
        rows = cur.fetchall()
        if not rows:
            break

        post_ids = [r[0] for r in rows]
        texts = [clean_text(r[1])[:1200] for r in rows]  # recorte duro por seguridad

        # Clasificar en lote
        results = clf(texts)

        # Preparar inserciones
        to_insert = []
        for pid, r in zip(post_ids, results):
            label = norm_label(r["label"])
            score = float(r["score"])
            to_insert.append((pid, PIPE_MODEL_NAME, label, score))

        # Upsert en scores
        cur.executemany("""
          INSERT OR REPLACE INTO scores (post_id, model_name, sentiment_label, sentiment_score)
          VALUES (?,?,?,?)
        """, to_insert)
        inserted_since_commit += len(to_insert)
        processed += len(to_insert)
        pbar.update(len(to_insert))

        # Commit periódico
        if inserted_since_commit >= COMMIT_EVERY:
            conn.commit()
            inserted_since_commit = 0

    # Commit final
    conn.commit()
    pbar.close()

print("✅ Clasificación completa.")
