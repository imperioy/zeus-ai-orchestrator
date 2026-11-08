from langchain_core.messages import HumanMessage, AIMessage

class GestorMemoria:
    def __init__(self):
        self.historial = []

    def agregar_interaccion(self, usuario, ia):
        self.historial.append(HumanMessage(content=usuario))
        self.historial.append(AIMessage(content=ia))

    def obtener_contexto(self):
        if not self.historial:
            return "No hay contexto previo."
        # Retorna solo los últimos 3 turnos (6 mensajes) para no saturar el token limit
        return "\n".join([f"{'Tú' if isinstance(m, HumanMessage) else 'Zeus'}: {m.content}" for m in self.historial[-6:]])