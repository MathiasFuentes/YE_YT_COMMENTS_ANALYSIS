# script: procesar_tematicas.py (Versión Mejorada con Progreso)

import pandas as pd
import sqlite3
from transformers import pipeline
import os
from tqdm import tqdm
import time

# --- CONFIGURACIÓN ---
DB_PATH = '../data/databaser.db'
print(f"Buscando DB en: {os.path.abspath(DB_PATH)}")
TABLA_POSTS = 'posts'
TABLA_SCORES = 'scores'
COL_TEXTO = 'text'
COL_SENTIMIENTO = 'sentiment_label'
COL_JOIN = 'post_id'
NUEVA_TABLA = "datos_finales_con_temas"

# ---------------------

# 1. Cargar el modelo
print("Cargando modelo Zero-Shot...")
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=0  # Forzar GPU (cuda:0)
)
print("Modelo cargado.")

# 2. Define las temáticas
tematicas_candidatas = [
    "Música", "Polémicas", "Familia", "Religión",
    "Entrevista con Joe Rogan", "Moda / Yeezy", "Política"
]

# 3. Conéctate a la DB y carga los datos
print(f"Conectando a {DB_PATH} y uniendo {TABLA_POSTS} y {TABLA_SCORES}...")
try:
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT
            t1.{COL_JOIN},
            t1.{COL_TEXTO},
            t2.{COL_SENTIMIENTO}
        FROM {TABLA_POSTS} AS t1
        INNER JOIN {TABLA_SCORES} AS t2 ON t1.{COL_JOIN} = t2.{COL_JOIN}
    """
    df = pd.read_sql_query(query, conn)
    print(f"✓ Datos cargados: {len(df)} comentarios en memoria.")
except Exception as e:
    print(f"Error al leer la base de datos: {e}")
    exit()

# --- PROCESAMIENTO CON PROGRESO ---
print(f"\nIniciando clasificación de {len(df)} comentarios...")
print("=" * 60)

# Limpiar textos
df[COL_TEXTO] = df[COL_TEXTO].fillna('').astype(str)
textos_lista = df[COL_TEXTO].tolist()

# Procesar en chunks con barra de progreso
BATCH_SIZE = 64
resultados_batch = []
tiempo_inicio = time.time()

# Dividir en chunks para mostrar progreso
num_chunks = (len(textos_lista) + BATCH_SIZE - 1) // BATCH_SIZE

print(f"Procesando en {num_chunks} batches de hasta {BATCH_SIZE} textos...")

for i in tqdm(range(0, len(textos_lista), BATCH_SIZE), 
              desc="Clasificando", 
              unit="batch",
              ncols=100):
    chunk = textos_lista[i:i+BATCH_SIZE]
    batch_resultado = classifier(
        chunk,
        tematicas_candidatas,
        multi_label=True
    )
    resultados_batch.extend(batch_resultado)
    
    # Mostrar ejemplo cada 500 batches
    if (i // BATCH_SIZE) % 500 == 0 and i > 0:
        ejemplo_idx = i
        print(f"\n  📝 Ejemplo [{ejemplo_idx}]: '{textos_lista[ejemplo_idx][:60]}...'")
        ejemplo = resultados_batch[ejemplo_idx]
        print(f"     Scores: {dict(zip(ejemplo['labels'][:3], [f'{s:.3f}' for s in ejemplo['scores'][:3]]))}")

tiempo_clasificacion = time.time() - tiempo_inicio
print(f"\n✓ Procesamiento completado en {tiempo_clasificacion/60:.2f} minutos")
print(f"  Velocidad: {len(textos_lista)/tiempo_clasificacion:.1f} textos/segundo")

# 5. Filtrar los resultados
print("\nFiltrando por umbral (0.30)...")
umbral = 0.30
tematicas_finales = []
temas_contador = {tema: 0 for tema in tematicas_candidatas}

for resultado in resultados_batch:
    if not isinstance(resultado, dict):
        tematicas_finales.append([])
        continue
    
    temas = [
        label for label, score in zip(resultado['labels'], resultado['scores'])
        if score > umbral
    ]
    
    # Contar temáticas
    for tema in temas:
        if tema in temas_contador:
            temas_contador[tema] += 1
    
    tematicas_finales.append(temas)

# 6. Mostrar estadísticas
print("\n" + "=" * 60)
print("ESTADÍSTICAS DE CLASIFICACIÓN:")
print("=" * 60)
for tema, count in sorted(temas_contador.items(), key=lambda x: x[1], reverse=True):
    porcentaje = (count / len(df)) * 100
    print(f"  {tema:25s}: {count:6d} comentarios ({porcentaje:5.2f}%)")

sin_tematica = sum(1 for t in tematicas_finales if len(t) == 0)
print(f"\n  Sin temática (< {umbral}):     {sin_tematica:6d} comentarios ({(sin_tematica/len(df))*100:5.2f}%)")

# Mostrar 5 ejemplos finales
print("\n" + "=" * 60)
print("EJEMPLOS DE CLASIFICACIÓN:")
print("=" * 60)
for i in range(min(5, len(df))):
    print(f"\n[{i+1}] Texto: '{df.iloc[i][COL_TEXTO][:80]}...'")
    print(f"    Temáticas: {tematicas_finales[i]}")
    print(f"    Sentimiento: {df.iloc[i][COL_SENTIMIENTO]}")

# 7. Asignar de vuelta al DataFrame
df['tematicas'] = tematicas_finales
df['tematicas'] = df['tematicas'].astype(str)

# 8. Guardar en la DB
print(f"\n{'='*60}")
print(f"Guardando resultados en la nueva tabla '{NUEVA_TABLA}'...")
try:
    df_final = df[['post_id', 'text', 'sentiment_label', 'tematicas']]
    df_final.to_sql(NUEVA_TABLA, conn, if_exists='replace', index=False)
    print(f"✓ ¡Proceso completado exitosamente!")
    print(f"✓ Tabla '{NUEVA_TABLA}' creada con {len(df_final)} registros")
except Exception as e:
    print(f"Error al guardar en la base de datos: {e}")
finally:
    conn.close()
    print(f"\n{'='*60}")
