

# Dashboard de Sentimiento (Kanye West)
Por Néstor Calderón y Matías Fuentes 
## Descripción

Aplicación multiparadigma que:

* Lee **comentarios reales de YouTube** (video *JRE #1554 – Kanye West*) ya cargados en **SQLite**.
* Usa clasificaciones de sentimiento **precalculadas** (`pos/neg/neu`) almacenadas en `scores`.
* Expone una **API Flask** (`/series`, `/kpis`, `/events`) y un **dashboard** (Chart.js).

> **No** necesitas clave de YouTube: la base `databaser.db` ya viene poblada.

---

## Estructura

```
YE_YT_COMMENTS_ANALYSIS/
├─ backend/
│  └─ app.py            # API Flask (series, kpis, events, health, _debug/db)
├─ scripts/             # (opcional) ingesta/clasificación usadas para construir la BD
├─ data/
│  └─ databaser.db      # SQLite con posts, scores, events, aggregates, etc.
├─ frontend/
│  └─ index.html        # Dashboard Chart.js (polar + línea + filtros)
└─ .env                 # Config (ruta BD y puerto)
```

---

## Requisitos

* Python 3.10+
* Dependencias (`pip install -r requirements.txt`)

  * Flask, flask-cors, python-dotenv, sqlite3 (stdlib), chart.js en el frontend (CDN)

---

## Configuración

Crea/edita **.env** en la raíz (sin API keys):

```env
# Ruta ABSOLUTA o relativa a la raíz del repo
DATABASE_URL=./data/databaser.db
FLASK_RUN_PORT=5000
```

---

## Ejecución

1. **Backend**

```bash
cd backend
flask run
# -> http://127.0.0.1:5000
```

2. **Frontend** (servidor estático)

```bash
cd frontend
python -m http.server 5500
# -> http://127.0.0.1:5500
```

3. **Endpoints útiles**

* `/kpis` → totales `{total_pos,total_neg,total_neu,total_comments}`
  filtros opcionales: `?from=YYYY-MM-DD&to=YYYY-MM-DD`
* `/series` → serie por día `{day,pos,neg,neu,total}` (soporta `from/to` si aplicaste el parche)
* `/events` → eventos `{event_date|date, tag, description, source_url}`

---

## Verificación rápida

* `/_debug/db` debe mostrar `db_exists: true` y tamaño > 0.
* `/kpis` debe devolver JSON con conteos reales (p.ej. 80 179 totales).
* En `frontend/index.html` verás **Polar Area** y **línea temporal** con filtros.

---

## Paradigmas aplicados

* **Imperativo/Procedimental:** ingesta y API paso a paso.
* **Estructurado:** pipeline modular (ingesta → análisis → DB → API → UI).
* **Funcional:** clasificación y agregaciones como funciones puras.
* **Declarativo:** SQL y configuración de Chart.js.
* **Reactivo (UI):** filtros (fecha/sentimiento) actualizan las vistas.

---

## Licencia y datos

* Datos almacenados en `SQLite` para fines académicos.
* No se requiere ni se distribuye clave de API.

