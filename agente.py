import os
import json
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ChatbotAgent:
    def __init__(self):
        # Fase 1: Inicialización Estática de Estados y Acciones
        self.estados = {
            "S0": ["hola", "buenas tardes", "buenos dias", "que tal", "saludos"],
            "S1": ["cuanto cuesta", "precio", "valor", "costo", "cotizacion"],
            "S2": ["adios", "chao", "hasta luego", "nos vemos", "despedida"],
            "S3": ["desconocido", "ayuda", "no entiendo"]
        }
        
        self.acciones = [
            "A0: ¡Hola! ¿En qué te puedo ayudar?",
            "A1: El precio es de 20 dólares.",
            "A2: ¡Adiós! Vuelve pronto.",
            "A3: ¿Puedes repetir? No te entendí bien."
        ]
        '''
        self.estados = {
            "S0": [
                "cuentame un chiste", "dime algo gracioso", "hazme reir", 
                "humor", "quiero un chiste ligero"
            ],
            "S1": [
                "que sabes de autos", "recomiendame un carro", "hablame de motores", 
                "automoviles", "que auto es bueno"
            ],
            "S2": [
                "que es la inteligencia artificial", "como funciona un llm", 
                "explicame machine learning", "ia", "que es q-learning"
            ],
            "S3": [
                "ver catalogo de productos", "que tienen a la venta", 
                "mostrar tienda", "comercio", "precios de productos"
            ],
            "S4": [
                "desconocido", "ayuda", "no entiendo", "cualquier otra cosa"
            ]
        }
        
        self.acciones = [
            "A0: ¿Por qué los pájaros no usan Facebook? ¡Porque ya tienen Twitter!",
            "A1: Te sugiero un sedán clásico con motor de 4 cilindros: confiable, ahorrador y fácil de reparar.",
            "A2: La IA es una rama de la informática que busca simular la inteligencia humana mediante algoritmos matemáticos.",
            "A3: En nuestro catálogo actual tenemos: Repuestos de autos ($50), Kits de Arduino ($25) y Libros de IA ($30).",
            "A4: Lo siento, mi base de datos matemática no logró procesar esa frase con claridad."
        ]
        '''
        
        # Hiperparámetros
        self.alpha = 0.5  # Tasa de aprendizaje
        self.epsilon = 0.3  # Tasa de exploración
        self.archivo_persistencia = "tabla_q.json"
        
        # Cargar o inicializar Tabla Q
        self.tabla_q = self._cargar_o_inicializar_tabla_q()
        
        # Fase 2: Configurar Intérprete TF-IDF
        self.vectorizer = TfidfVectorizer()
        self._entrenar_interprete()

    def _cargar_o_inicializar_tabla_q(self):
        """Lee la tabla Q desde JSON o la crea si no existe."""
        if os.path.exists(self.archivo_persistencia):
            with open(self.archivo_persistencia, "r") as f:
                return json.load(f)
        else:
            # Inicializar matriz en 0.00
            nueva_tabla = {s: {a: 0.00 for a in self.acciones} for s in self.estados.keys()}
            self._guardar_tabla_q(nueva_tabla)
            return nueva_tabla

    def _guardar_tabla_q(self, tabla=None):
        """Guarda el estado actual de la Tabla Q en la persistencia JSON."""
        data_a_guardar = tabla if tabla is not None else self.tabla_q
        with open(self.archivo_persistencia, "w") as f:
            json.dump(data_a_guardar, f, indent=4)

    def _entrenar_interprete(self):
        """Prepara el corpus para el cálculo de similitud del coseno."""
        self.corpus_estados = []
        self.mapeo_corpus_a_estado = []
        
        for estado, frases in self.estados.items():
            for frase in frases:
                self.corpus_estados.append(frase)
                self.mapeo_corpus_a_estado.append(estado)
                
        self.vectorizer.fit(self.corpus_estados)

    def clasificar_estado(self, texto_usuario):
        """Fase 2: Evalúa la entrada del usuario usando Similitud del Coseno."""
        texto_limpio = texto_usuario.lower().strip()
        if not texto_limpio:
            return "S3"
            
        # Transformar a vectores TF-IDF
        vector_usuario = self.vectorizer.transform([texto_limpio])
        vectores_corpus = self.vectorizer.transform(self.corpus_estados)
        
        # Calcular similitudes
        similitudes = cosine_similarity(vector_usuario, vectores_corpus).flatten()
        indice_max = np.argmax(similitudes)
        
        # Si la similitud es extremadamente baja o cero, mapear a S3 (Desconocido)
        if similitudes[indice_max] < 0.15:
            return "S3"
            
        return self.mapeo_corpus_a_estado[indice_max]

    def seleccionar_accion(self, estado):
        """Fase 3: Selección de la acción usando la estrategia Epsilon-Greedy."""
        numero_aleatorio = random.random()
        
        if numero_aleatorio <= self.epsilon:
            # Exploración: Acción al azar
            accion = random.choice(self.acciones)
            metodo = "Exploración (Azar)"
        else:
            # Explotación: Acción con mayor valor Q
            acciones_estado = self.tabla_q[estado]
            # Manejar empates de forma aleatoria
            max_valor = max(acciones_estado.values())
            mejores_acciones = [a for a, v in acciones_estado.items() if v == max_valor]
            accion = random.choice(mejores_acciones)
            metodo = "Explotación (Tabla Q)"
            
        return accion, metodo

    def actualizar_aprendizaje(self, estado, accion, recompensa):
        """Fase 5: Actualización matemática (Ecuación de Bellman simplificada)."""
        q_anterior = self.tabla_q[estado][accion]
        
        # Fórmula aplicada: Q(S,A) = Q(S,A) + alpha * [R - Q(S,A)]
        nuevo_q = q_anterior + self.alpha * (recompensa - q_anterior)
        
        # Guardar en memoria y persistencia
        self.tabla_q[estado][accion] = round(nuevo_q, 4)
        self._guardar_tabla_q()
        
        # Retornar detalles para el registro de logs de la interfaz
        log_formula = f"Q({estado}, {accion[:2]}) = {q_anterior} + {self.alpha} * [{recompensa} - {q_anterior}]"
        log_resultado = f"Nuevo Q = {self.tabla_q[estado][accion]}"
        
        return log_formula, log_resultado