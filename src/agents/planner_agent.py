from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from src.config.llm_manager import obtener_llm_robusto

# 1. Definimos la estructura exacta que queremos que devuelva la IA
class Tarea(BaseModel):
    agente_asignado: str = Field(description="Nombre del rol especializado para la tarea (ej. Buscador, Analista_Datos, Lector_PDF, Ejecutor_Python, Escritor_Archivos)")
    instruccion: str = Field(description="Instrucción detallada y específica que este agente debe ejecutar utilizando sus herramientas")

class PlanDeAccion(BaseModel):
    tareas: List[Tarea] = Field(description="Lista de tareas a ejecutar en paralelo o secuencialmente para resolver la petición")

# 2. Creamos el agente planificador
def crear_planificador():
    # Instanciamos nuestro motor blindado (Google 1 -> Google 2 -> Ollama)
    llm_blindado = obtener_llm_robusto(temperatura=0)
    
    # Diseñamos el prompt maestro
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres el Orquestador Maestro de un sistema multi-agente avanzado.
        Tu trabajo es analizar la petición del usuario y dividirla en un plan de acción con tareas específicas.
        
        El sistema cuenta con las siguientes capacidades reales a través de herramientas:
        - buscar_internet (Wikipedia)
        - listar_directorio y leer_archivo (Exploración local)
        - leer_pdf (Extracción de texto PDF)
        - ejecutar_codigo_python (Cálculos y algoritmos)
        - ejecutar_comando_sistema (Terminal/PowerShell/Bash)
        - leer_url (Web scraping y lectura de páginas web)
        - analizar_imagen (Visión artificial para png/jpg)
        - guardar_en_memoria / buscar_en_memoria (Memoria vectorial)
        - escribir_archivo_seguro (Crear/modificar archivos)
        
        Genera un plan lógico. Si las tareas son independientes (ej. "Busca X y también lee el archivo Y"), 
        créalas como tareas separadas para que el sistema multihilo las ejecute simultáneamente."""),
        ("human", "{solicitud}")
    ])
    
    # Unimos el prompt al modelo forzando la salida estructurada de Pydantic
    planificador = prompt | llm_blindado.with_structured_output(PlanDeAccion)
    
    return planificador