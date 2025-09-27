# Scraper + Analítica Web: Análisis de Sentimiento sobre Kanye West

##  Descripción
Este proyecto corresponde al **Proyecto final de la asignatura Paradigmas de Programación**.  
El objetivo es desarrollar una **aplicación web multiparadigma** que permita recolectar publicaciones reales desde la red social **X (antes Twitter)**, procesarlas mediante **NLP (análisis de sentimiento)** y visualizar de forma interactiva la **evolución del sentimiento público** hacia una figura controversial, en este caso **Kanye West**, durante el periodo **2020–2022**.  

El proyecto integra distintos **paradigmas de programación**:  
- **Orientado a Objetos (POO):** para modelar entidades como Tweet, Usuario y Analizador de Sentimiento.  
- **Funcional:** para implementar el pipeline de procesamiento de texto (limpieza → análisis → clasificación).  
- **Estructurado (procedural):** para la orquestación de tareas de scraping, almacenamiento y visualización.  

Se busca no solo mostrar “qué opina la gente”, sino también analizar la **dinámica temporal**, la **intensidad de interacciones** y la **relación con eventos relevantes** (noticias, lanzamientos o controversias).

---

## Instrucciones de ejecución

> Nota: estas instrucciones son preliminares y se irán ajustando a medida que avance el desarrollo.

1. **Clonar el repositorio**  
   ```bash
   git clone <https://github.com/MathiasFuentes/ye_x_analysis>
   cd <carpeta-del-repo>
    ````

2. **Crear un entorno virtual e instalar dependencias**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows

   pip install -r requirements.txt
   ```

3. **Ejecutar el scraper para recolectar datos**

   * El scraper usa [`snscrape`](https://github.com/JustAnotherArchivist/snscrape) para obtener tweets reales sobre Kanye West (2020–2022).
   * Los resultados se almacenan en formato **CSV** dentro de la carpeta `data/`.

4. **Procesar los datos con NLP**

   * Se aplicará un modelo preentrenado de análisis de sentimiento (`cardiffnlp/twitter-roberta-base-sentiment-latest`).
   * El procesamiento generará nuevas columnas (`sentiment_label`, `sentiment_score`).

5. **Visualizar resultados**

    * Se incluirá un dashboard web interactivo desarrollado con Flask y Chart.js, que mostrará:

    *   Evolución del sentimiento en el tiempo (positivo, negativo y neutro).

    * Volumen de interacciones (likes, retweets, respuestas, citas).

    * Eventos destacados en la línea de tiempo, relacionados con la actividad y controversias de Kanye West.

---

##  Integrantes

* **Matías Fuentes**
* **Néstor Calderón**
* **Sofía Ríos**

---

##  Licencia y uso de datos

* Los datos recolectados provienen de la red social **X (antes Twitter)** a través de `snscrape`.
* En cumplimiento de los **Términos de Servicio de X**, este repositorio no compartirá texto crudo de los tweets.
* Se publicarán únicamente **IDs de tweets y métricas agregadas**, suficientes para fines académicos.
