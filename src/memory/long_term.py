import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

class GestorMemoriaLargoPlazo:
    def __init__(self, directorio_db="./data/vector_db"):
        # Usamos un modelo local ultraligero y rápido para transformar texto en vectores
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.directorio_db = directorio_db
        
        # Asegurarnos de que el directorio existe
        os.makedirs(self.directorio_db, exist_ok=True)
        
        # Inicializar la base de datos vectorial local (ChromaDB)
        self.vector_store = Chroma(
            collection_name="zeus_memory",
            embedding_function=self.embeddings,
            persist_directory=self.directorio_db
        )

    def guardar_recuerdo(self, texto: str, categoria: str = "general"):
        """Guarda un fragmento de conocimiento permanente en el sistema."""
        doc = Document(page_content=texto, metadata={"categoria": categoria})
        self.vector_store.add_documents([doc])
        return f"Recuerdo guardado con éxito en la categoría '{categoria}'."

    def buscar_recuerdo(self, consulta: str, k: int = 2) -> str:
        """Busca en la base de datos la información más parecida a la consulta."""
        resultados = self.vector_store.similarity_search(consulta, k=k)
        if not resultados:
            return "No hay recuerdos a largo plazo sobre este tema."
        
        textos = [f"- {res.page_content}" for res in resultados]
        return "Conocimiento previo recuperado:\n" + "\n".join(textos)