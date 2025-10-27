# Scraper + Analítica Web: Análisis de Sentimiento sobre Kanye West

##  Descripción
Este proyecto corresponde al **Proyecto final de la asignatura Paradigmas de Programación**.  
Su objetivo es desarrollar una aplicación web multiparadigma que permita lo siguiente:
- Recolectar comentarios reales desde YouTube (video Joe Rogan Experience #1554 – Kanye West).
- Procesarlos mediante un modelo RoBERTa de análisis de sentimiento.

- Almacenarlos y agregarlos en una base de datos SQLite.

- Visualizar de forma interactiva la evolución temporal del sentimiento y su relación con  eventos mediáticos relevantes.
  
---
El proyecto integra distintos **paradigmas de programación**:  
- **Imperativo / Procedimental:**
  Ingesta y clasificación implementadas paso a paso en scripts Python     (staging_insert_yt.py, score_all_roBERTa.py).
  
- **Estructurado:** Pipeline modularizado en etapas (ingesta → análisis → agregación → visualización).
  
- **Funcional:** Clasificación con funciones puras y transformaciones sin efectos colaterales.

- **Declarativo:** Uso extensivo de SQL y Chart.js para expresar qué se quiere obtener, no cómo implementarlo.

- **Reactivo (Frontend):** El dashboard reacciona a cambios de filtros de fecha y tipo de sentimiento.

Se busca no solo mostrar “qué opina la gente”, sino también analizar la **dinámica temporal**, la **intensidad de interacciones** y la **relación con eventos relevantes** (noticias, lanzamientos o controversias).

---
### Arquitectura General

La arquitectura del sistema se basa en una estructura modular donde cada componente cumple una función específica dentro del flujo de procesamiento de datos:
```bash
YouTube API → staging_insert_yt.py 
               ↓
    SQLite (databaser.db)
               ↓
score_all_roBERTa.py (clasificación RoBERTa)
               ↓
   app.py (API Flask REST)
               ↓
   Frontend (Chart.js + HTML + JS)
````
Descripción del flujo:

1. YouTube API: se utiliza para extraer datos (por ejemplo, títulos, comentarios o metadatos de videos).

2. staging_insert_yt.py: recibe los datos de la API y los inserta en la base de datos local SQLite (databaser.db).

3. score_all_roBERTa.py: toma los registros almacenados y ejecuta el modelo RoBERTa para clasificar o analizar los textos (por ejemplo, detectar sentimiento o temática).

4. app.py: implementa una API REST con Flask, que expone los resultados del análisis al frontend.

5. Frontend: muestra los datos procesados mediante Chart.js y tecnologías web (HTML, JS), permitiendo visualizar métricas y resultados de forma interactiva.

---
En el siguiente apartado se detalla el origen y características de los datos utilizados en el proyecto.
Los comentarios analizados provienen directamente de la API oficial de YouTube, extraídos del video “Joe Rogan Experience #1554 – Kanye West”, publicado en el canal PowerfulJRE.

### Dataset

- Fuente: API oficial de YouTube.

- Video: Joe Rogan Experience #1554 – Kanye West.

- Volumen: +80.000 comentarios procesados.

- Formato: Base de datos SQLite (databaser.db) con tablas:

   - posts — comentarios brutos

   - scores — análisis de sentimiento (pos, neg, neu)

   - events — hitos mediáticos de Kanye West

La recolección se realizó mediante un script propio (staging_insert_yt.py) que utiliza la YouTube Data API v3 para obtener información pública de los comentarios, incluyendo:

- Texto del comentario

- Fecha de publicación

- Autor (anónimo o seudónimo)

- Identificador del comentario

- Identificador del video

Estos datos se almacenan localmente en una base de datos SQLite, dentro de la tabla posts, para su posterior procesamiento.
Posteriormente, cada comentario se somete a un análisis de sentimiento mediante el modelo RoBERTa (roberta-base), generando etiquetas de sentimiento positivas, negativas y neutras, que se guardan en la tabla scores.

El dataset final, por tanto, es una versión enriquecida de los comentarios originales de YouTube, que combina datos reales obtenidos de la plataforma con resultados inferidos por el modelo de lenguaje.
Todo el proceso respeta las políticas de uso de datos de la API de YouTube, utilizando únicamente información pública con fines académicos y de investigación.


---

## Instrucciones de ejecución

> Nota: estas instrucciones son preliminares y se irán ajustando a medida que avance el desarrollo.

1. **Clonar el repositorio**  
   ```bash
   git clone <URL_DEL_REPO>
   cd YE_YT_COMMENTS_ANALYSIS
    ````

2. **Crear un entorno virtual e instalar dependencias**

   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Linux/Mac
   .venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   Crea un archivo .env en la raíz:
   ```bash
   DATABASE_URL=./data/databaser.db
   YOUTUBE_API_KEY=TU_API_KEY
   FLASK_RUN_PORT=5000
   ```
4. **Ejecutar ingesta de comentarios**
   ```bash
   python scripts/staging_insert_yt.py
   ```
5. **Ejecutar análisis de sentimiento**
   ```bash
   python scripts/score_all_roBERTa.py
   ```
6. **Levantar la API Flask**
   ```bash
   cd backend
   flask run
   ```
---

### Endpoints Disponibles (API REST)
La API desarrollada en Flask expone varios endpoints que permiten acceder a los datos procesados y a los resultados de análisis generados por el modelo RoBERTa.
Cada endpoint entrega información específica en formato JSON, pensada para ser consumida por el frontend (Chart.js + JS).
| Endpoint  | Descripción                                                   | Ejemplo       |
| --------- | ------------------------------------------------------------- | ------------- |
| `/series` | Serie temporal de sentimientos (pos/neg/neu) agrupada por día | `GET /series` |
| `/kpis`   | Totales agregados de sentimiento                              | `GET /kpis`   |
| `/events` | Eventos mediáticos cargados manualmente                       | `GET /events` |

Resumen visual del flujo:
```bash
Frontend (Chart.js + JS)
        ↓ consume
     Flask API (app.py)
        ├── /series  → datos diarios de sentimiento
        ├── /kpis    → métricas globales
        └── /events  → eventos cargados manualmente
```

### Frontend (Próxima etapa)

La siguiente fase del proyecto contempla el desarrollo de un dashboard interactivo que permitirá visualizar los resultados del análisis de sentimientos de manera dinámica y comprensible para el usuario final.
El frontend estará implementado con Chart.js, HTML y JavaScript, integrándose con la API Flask para obtener los datos procesados desde la base de datos.

Componentes principales del dashboard:
- Línea temporal (POS / NEG / NEU): gráfico de líneas que muestra la evolución diaria de los sentimientos.

- Eventos en timeline: uso del annotation plugin de Chart.js para marcar eventos mediáticos sobre la línea temporal.

- Gráfico de área polar: muestra la distribución general de los sentimientos.

- Filtros interactivos: permiten seleccionar rangos de fecha y tipo de sentimiento para actualizar las visualizaciones en tiempo real.

Esquema visual:
```
Dashboard (Chart.js + HTML + JS)
        ↓ consume
     Flask API (app.py)
        ↓
   Datos procesados (SQLite + RoBERTa)
```

---

##  Integrantes

* **Matías Fuentes**
* **Néstor Calderón**

---

##  Licencia y uso de datos
- Los datos provienen de YouTube API.

- Se respetan las políticas de uso de datos de YouTube.

- El dataset no incluye información sensible ni texto crudo más allá de lo necesario para análisis     académico.


