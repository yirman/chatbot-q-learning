# Chatbot Q-Learning

Chatbot interactivo que aprende de las evaluaciones del usuario mediante un algoritmo de **Q-Learning**.

## ¿Cómo funciona?

1. **Clasificación de intención** — El mensaje del usuario se convierte en un vector TF-IDF y se compara con frases de referencia usando similitud del coseno. La frase más cercana determina el estado (S0–S3).
2. **Selección de acción** — El agente usa una estrategia *epsilon-greedy*: con probabilidad ε elige una respuesta al azar (exploración), y en caso contrario elige la respuesta con mayor valor Q (explotación).
3. **Feedback del usuario** — Tras cada respuesta, el usuario puede calificarla con **Like (+1)** o **Dislike (-1)**.
4. **Actualización de la Tabla Q** — Con cada evaluación se aplica la ecuación de Bellman simplificada:

   ```
   Q(S,A) = Q(S,A) + α × [R - Q(S,A)]
   ```

   Donde α es la tasa de aprendizaje y R es la recompensa recibida.

5. **Persistencia** — La tabla Q se guarda automáticamente en `tabla_q.json`, por lo que el aprendizaje persiste entre ejecuciones.

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Dependencias: `numpy`, `scikit-learn`, `flet`.

## Ejecución

Interfaz moderna (Flet):

```bash
python flet_ui.py
```

Interfaz clásica (Tkinter):

```bash
source venv/bin/activate
python main.py
```
