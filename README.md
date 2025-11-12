# Kanye West: Análisis de Sentimiento y Temáticas

Dashboard interactivo de sentimiento y temáticas sobre Kanye West. Analiza +80,000 comentarios usando un backend de Flask, frontend con Chart.js y un modelo NLP (Hugging Face) para la clasificación de temas.

## Sobre el Proyecto

Este proyecto analiza más de 80,000 comentarios de YouTube para visualizar la percepción pública sobre Kanye West. El dashboard está dividido en dos secciones principales:

*   **Panel Principal (Visión Histórica):** Muestra el análisis de sentimiento y temáticas de *todo el conjunto de datos* (2020-2025).
*   **Panel de Comparación (Visión Específica):** Permite al usuario seleccionar eventos clave específicos y sumariza el impacto de sentimiento (Pos/Neg/Neu) en los 30 días posteriores a dichos eventos.

## Features

### Panel Principal
* **KPIs Globales:** Métricas clave (Total, Pos, Neg, Neu) y un "Net Sentiment Score" (Sentimiento Neto) para todo el período.
* **Distribución de Sentimiento:** Un gráfico de dona que muestra la proporción general de sentimientos.
* **Análisis de Temáticas:** Un gráfico de barras horizontales apiladas que desglosa los temas más discutidos (Música, Polémicas, etc.) y su composición de sentimiento.
* **Descripciones de Modelos:** Textos de referencia que explican qué modelos de NLP se usaron para obtener los datos (`roBERTa` y `facebook/bart-large-mnli`).

### Sección de Comparativa de Eventos
* **Lista de Eventos (Checkboxes):** Una lista completa de eventos clave en la carrera de Kanye.
* **Selección Múltiple:** Permite seleccionar uno o más eventos para comparar.
* **Gráfico Pie de Impacto:** Un gráfico de torta dinámico que **suma** los datos de sentimiento (Pos/Neg/Neu) de los 30 días posteriores a cada evento seleccionado, mostrando el impacto agregado.
* **Estado Cero:** Si no se selecciona ningún evento, el gráfico muestra un estado gris ("Sin selección").

---

## Tech Stack

### Backend y Procesamiento de Datos
* **Python 3**
* **Flask:** Para servir la API REST.
* **Flask-CORS:** Para manejar las peticiones de origen cruzado desde el frontend.
* **Pandas:** Para agregaciones de datos rápidas en la API.
* **SQLite:** Como base de datos para almacenar comentarios, sentimientos y temáticas.
* **Hugging Face transformers:**
    * `roBERTa`: Para la clasificación de sentimiento (`pos`, `neg`, `neu`) en la tabla `scores`.
    * `facebook/bart-large-mnli`: Para la clasificación de temáticas (Zero-Shot) en el script de pre-procesamiento.

### Frontend
* **HTML5**
* **CSS3** (Moderno, estilo "dark mode")
* **JavaScript (ES6+):** Vanilla JS con `fetch` y funciones `async/await`.
* **Chart.js:** Para todas las visualizaciones de datos (Dona, Barras y Torta).
* **Luxon.js:** Para el cálculo de los rangos de fechas de 30 días.

---

## Estructura del Proyecto

```
├── backend/
│   └── app.py              \# API de Flask (endpoints /kpis, /topics)
├── data/
│   └── databaser.db        \# Base de datos SQLite (pre-procesada)
├── frontend/
│   └── index.html          \# El dashboard principal
├── scripts/                \# Scripts de pre-procesamiento (ej. NLP)
└── requirements.txt
````

---
## Previo a la Ejecución

Este proyecto utiliza un archivo grande de base de datos (databaser.db) almacenado con Git LFS (Large File Storage), es decir, el archivo descargado no es la base real, sino un puntero de Git LFS.
Desde la carpeta raíz del proyecto, descarga la db de la siguiente forma:

**Para usar Git LFS, es obligatorio usar clonar el repositorio desde su comando correspondiente:**
```bash
#Previo: Clonar el repo
git clone https://github.com/MathiasFuentes/YE_YT_COMMENTS_ANALYSIS.git

# 1. Instalar Git LFS
git lfs install

# 2. Descargar DB
git lfs pull
```
Con esto, Flask podrá leer correctamente la base de datos y el backend funcionará sin errores.

## Cómo Ejecutarlo

### 1. Iniciar el Backend (API de Flask)

El backend sirve los datos desde la base de datos.

```bash
1. Navega a la carpeta del backend
# cd backend

2. (Recomendado) Crea un entorno virtual
# python -m venv venv

En Windows:
# venv\Scripts\activate
En macOS/Linux:
# source venv/bin/activate

3. Instala los requerimientos
# pip install -r requirements.txt

4. Inicia el servidor
# python app.py
````

El servidor del backend se ejecutará en `http://127.0.0.1:5000`

### 2\. Iniciar el Frontend

El frontend es un archivo estático y debe servirse desde un puerto diferente.

```bash
1. Abre OTRA terminal
2. Navega a la carpeta del frontend
# cd frontend

3. Inicia un servidor web simple
python -m http.server 5500
```

El frontend estará disponible en `http://localhost:5500`

¡Abre **`http://localhost:5500`** en tu navegador para ver el dashboard\!
