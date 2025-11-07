# script: revisar_db.py
import sqlite3
import os

# --- RUTA CORREGIDA ---
DB_PATH = '../data/databaser.db'
# ---------------------

print(f"Buscando la base de datos en: {os.path.abspath(DB_PATH)}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("\n¡Conexión exitosa!")

    print("\n--- Conteo de Filas por Tabla ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()

    if not tablas:
        print("Tu base de datos está vacía.")
    else:
        for tabla in tablas:
            table_name = tabla[0]
            
            # Ignorar tablas internas de SQLite
            if table_name == 'sqlite_sequence':
                continue
            
            # Contar filas en la tabla
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"\nTabla: '{table_name}' --- Filas: {count}")
            
            # Si la tabla tiene datos, mostrar sus columnas
            if count > 0:
                print(f"  Columnas en '{table_name}':")
                cursor.execute(f"PRAGMA table_info({table_name})")
                columnas = cursor.fetchall()
                for col in columnas:
                    print(f"    - Nombre: {col[1]}, Tipo: {col[2]}")
                    
    conn.close()

except Exception as e:
    print(f"\n--- ERROR ---")
    print(f"Error al conectar o leer la DB: {e}")