import tkinter as tk
from tkinter import ttk, messagebox
from agente import ChatbotAgent

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UNEG - Chatbot Interactivo (Q-Learning)")
        self.root.geometry("950x600")
        self.root.configure(bg="#f4f6f9")
        
        # Inicializar el agente inteligente
        self.agente = ChatbotAgent()
        
        # Variables de estado de interacción temporal
        self.estado_actual = None
        self.accion_actual = None
        
        self._construir_interfaz()
        self._actualizar_vista_tabla_q()

    def _construir_interfaz(self):
        # Estilos visuales sencillos
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        
        # Contenedor Principal Izquierdo: Chat e Interacción
        frame_izq = tk.Frame(self.root, bg="#f4f6f9", width=450)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Ventana de Chat
        tk.Label(frame_izq, text="Chat de Interacción", font=("Helvetica", 12, "bold"), bg="#f4f6f9").pack(anchor=tk.W)
        self.txt_chat = tk.Text(frame_izq, height=18, width=50, state=tk.DISABLED, wrap=tk.WORD, font=("Helvetica", 10))
        self.txt_chat.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Entrada de Texto y Botón Enviar
        frame_entrada = tk.Frame(frame_izq, bg="#f4f6f9")
        frame_entrada.pack(fill=tk.X, pady=5)
        
        self.entry_mensaje = tk.Entry(frame_entrada, font=("Helvetica", 11))
        self.entry_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.entry_mensaje.bind("<Return>", lambda event: self._procesar_envio())
        
        self.btn_enviar = ttk.Button(frame_entrada, text="Enviar", command=self._procesar_envio)
        self.btn_enviar.pack(side=tk.RIGHT, padx=5)
        
        # Panel de Feedback (Fase 4: Feedback del usuario)
        self.frame_feedback = tk.LabelFrame(frame_izq, text="Evalúa la respuesta del Bot", font=("Helvetica", 10, "bold"), bg="#f4f6f9")
        self.frame_feedback.pack(fill=tk.X, pady=10)
        
        self.btn_like = tk.Button(self.frame_feedback, text="👍 Like (+1)", bg="#d4edda", fg="#155724", font=("Helvetica", 10, "bold"), state=tk.DISABLED, command=lambda: self._procesar_recompensa(1))
        self.btn_like.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
        
        self.btn_dislike = tk.Button(self.frame_feedback, text="👎 Dislike (-1)", bg="#f8d7da", fg="#721c24", font=("Helvetica", 10, "bold"), state=tk.DISABLED, command=lambda: self._procesar_recompensa(-1))
        self.btn_dislike.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10, pady=8)
        
        # Contenedor Principal Derecho: Tabla Q y Logs Matemáticos
        frame_der = tk.Frame(self.root, bg="#f4f6f9", width=450)
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Visualización Matriz Tabla Q
        tk.Label(frame_der, text="Tabla Q (Estado vs Acción)", font=("Helvetica", 12, "bold"), bg="#f4f6f9").pack(anchor=tk.W)
        
        columnas = ["Estado"] + [f"A{i}" for i in range(len(self.agente.acciones))]
        self.tabla_vista = ttk.Treeview(frame_der, columns=columnas, show="headings", height=6)
        self.tabla_vista.pack(fill=tk.X, pady=5)
        
        # Configurar anchos de columna de la matriz gráfica
        self.tabla_vista.heading("Estado", text="Estado")
        self.tabla_vista.column("Estado", width=70, anchor=tk.CENTER)
        for i, acc in enumerate(self.agente.acciones):
            col_id = f"A{i}"
            self.tabla_vista.heading(col_id, text=col_id)
            self.tabla_vista.column(col_id, width=85, anchor=tk.CENTER)
            
        # Panel del Log de Operaciones (Ecuación de Bellman)
        tk.Label(frame_der, text="Log Matemático (Ecuación de Bellman)", font=("Helvetica", 12, "bold"), bg="#f4f6f9").pack(anchor=tk.W, pady=(10,0))
        self.txt_log = tk.Text(frame_der, height=10, width=50, bg="#212529", fg="#00ff00", font=("Consolas", 10), state=tk.DISABLED)
        self.txt_log.pack(fill=tk.BOTH, expand=True, pady=5)
        self._escribir_log(">> Sistema inicializado. Esperando interacción del usuario...")

    def _imprimir_en_chat(self, emisor, mensaje):
        self.txt_chat.config(state=tk.NORMAL)
        self.txt_chat.insert(tk.END, f"{emisor}: {mensaje}\n\n")
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state=tk.DISABLED)

    def _escribir_log(self, mensaje):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert(tk.END, f"{mensaje}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state=tk.DISABLED)

    def _actualizar_vista_tabla_q(self):
        """Sincroniza visualmente los cambios de la matriz JSON en pantalla."""
        for row in self.tabla_vista.get_children():
            self.tabla_vista.delete(row)
            
        for estado, acciones_valores in self.agente.tabla_q.items():
            valores_fila = [estado]
            for acc in self.agente.acciones:
                valores_fila.append(f"{acciones_valores[acc]:.4f}")
            self.tabla_vista.insert("", tk.END, values=valores_fila)

    def _procesar_envio(self):
        mensaje = self.entry_mensaje.get().strip()
        if not mensaje:
            return
            
        self._imprimir_en_chat("Tú", mensaje)
        self.entry_mensaje.delete(0, tk.END)
        
        # Bloquear el botón de envío hasta que el usuario califique la respuesta actual
        self.btn_enviar.config(state=tk.DISABLED)
        self.entry_mensaje.config(state=tk.DISABLED)
        
        # Fase 2: Mapeo de intención
        self.estado_actual = self.agente.clasificar_estado(mensaje)
        
        # Fase 3: Tomar decisión (Epsilon-Greedy)
        self.accion_actual, metodo_seleccion = self.agente.seleccionar_accion(self.estado_actual)
        
        # Fase 4: Mostrar Respuesta
        self._imprimir_en_chat("Bot", self.accion_actual)
        
        # Log del paso actual
        self._escribir_log(f"\n[Interacción] Entrada clasificada como Estado: {self.estado_actual}")
        self._escribir_log(f"[Decisión] Acción elegida vía: {metodo_seleccion}")
        self._escribir_log(f">> Esperando evaluación del usuario...")
        
        # Activar botones de feedback
        self.btn_like.config(state=tk.NORMAL)
        self.btn_dislike.config(state=tk.NORMAL)

    def _procesar_recompensa(self, valor_recompensa):
        # Desactivar botones de feedback
        self.btn_like.config(state=tk.DISABLED)
        self.btn_dislike.config(state=tk.DISABLED)
        
        # Fase 5: Ejecutar actualización y persistencia
        log_formula, log_resultado = self.agente.actualizar_aprendizaje(
            self.estado_actual, self.accion_actual, valor_recompensa
        )
        
        # Actualizar componentes de la GUI
        self._actualizar_vista_tabla_q()
        self._escribir_log(f"[Recompensa Recibida] R = {valor_recompensa}")
        self._escribir_log(f"[Fórmula] {log_formula}")
        self._escribir_log(f"[Resultado] {log_resultado}")
        
        # Mostrar en el chat la evaluación resumida
        eval_str = "+1 (Like)" if valor_recompensa == 1 else "-1 (Dislike)"
        self._imprimir_en_chat("Sistema", f"Respuesta evaluada con recompensa: {eval_str}")
        
        # Habilitar entrada para el siguiente ciclo
        self.btn_enviar.config(state=tk.NORMAL)
        self.entry_mensaje.config(state=tk.NORMAL)
        self.entry_mensaje.focus()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()