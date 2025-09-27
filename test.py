from transformers import pipeline
from transformers.utils import logging
# Evitar warnings de RoBERTa
logging.set_verbosity_error()

# Ejemplos de tweets sobre YE dados por GPT5
tweets = [
    "Kanye West is a musical genius, his old albums are timeless!",
    "I'm so tired of Kanye's drama... every week there's a new controversy.",
    "Respect to Ye for speaking his mind, even if people disagree.",
    "Kanye spreading hate again, this is disgusting and dangerous.",
    "Just bought Yeezys 👟🔥 Kanye really changed sneaker culture forever.",
    "Sometimes I can't tell if Kanye is brilliant or completely lost.",
    "Ye should focus on music instead of politics and nonsense.",
    "I love how Kanye always pushes creativity beyond the limit.",
    "Kanye's comments today were offensive and disappointing.",
    "Say what you want, but no one innovates like Kanye West."
]

# Ejecutar pipeline de análisis de sentimiento y guardar los resultados
classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
results = classifier(tweets, batch_size=8, truncation=True)

# Mostrar análisis por cada uno de los tweets
for tweet, res in zip(tweets, results):
    print(f"{tweet}\n -> {res}\n")

# Resumen rápido -> 'S': N.
# S es el sentimiento identificado, N es el número de veces que apareció.
labels = [res["label"] for res in results]
summary = {label: labels.count(label) for label in set(labels)}
print("Resumen:", summary)