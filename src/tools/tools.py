import os
import shutil
import wikipedia
import subprocess
import requests
import google.generativeai as genai
from PIL import Image
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_experimental.utilities import PythonREPL
from langchain_community.document_loaders import PyPDFLoader
# Importamos el gestor de memoria a largo plazo que acabas de crear
from src.memory.long_term import GestorMemoriaLargoPlazo
from bs4 import BeautifulSoup
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Instanciamos el intérprete de Python globalmente
python_repl = PythonREPL()

load_dotenv()
wikipedia.set_lang("es") # Configurar búsqueda en español

# Inicializamos la memoria a largo plazo globalmente para que las herramientas la usen
memoria_largo_plazo = GestorMemoriaLargoPlazo()

@tool
def buscar_internet(consulta: str) -> str:
    """Busca información verificada y conocimiento general en internet."""
    print(f"\n[🔍 WIKIPEDIA] Interceptando petición de búsqueda: '{consulta}'...")
    try:
        resultados = wikipedia.search(consulta)
        if not resultados:
            print("[🔍 WIKIPEDIA] ❌ No hay resultados.")
            return f"No se encontró absolutamente nada sobre '{consulta}'."
        
        mejor_opcion = resultados[0]
        print(f"[🔍 WIKIPEDIA] ✔️ Mejor coincidencia encontrada: '{mejor_opcion}'. Extrayendo resumen...")
        
        resumen = wikipedia.summary(mejor_opcion, sentences=3, auto_suggest=False)
        # INYECCIÓN DIRECTA: Obligamos al modelo a transcribir
        return f"ÓRDEN ESTRICTA: Debes copiar y pegar el siguiente texto literalmente en tu respuesta final, sin resumirlo:\n\n{resumen}"
        
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"[🔍 WIKIPEDIA] ⚠️ Término ambiguo, probando alternativa: '{e.options[0]}'")
        try:
            resumen_alt = wikipedia.summary(e.options[0], sentences=3, auto_suggest=False)
            return f"ÓRDEN ESTRICTA: Debes copiar y pegar el siguiente texto literalmente en tu respuesta final, sin resumirlo:\n\n{resumen_alt}"
        except Exception as ex:
            return f"Error de desambiguación al extraer texto: {ex}"
    except Exception as e:
        print(f"[🔍 WIKIPEDIA] ❌ Error técnico de conexión: {e}")
        return f"Error técnico en la búsqueda de Wikipedia: {e}"

@tool
def escribir_archivo_seguro(ruta: str, contenido: str) -> str:
    """Escribe o modifica un archivo local. NUNCA se ejecuta sin la clave de acción del usuario."""
    print(f"\n[⚠️ ALERTA DE SEGURIDAD] El agente solicita modificar/crear el archivo: {ruta}")
    clave_accion = os.getenv("ACTION_KEY")
    
    if not clave_accion:
        return "Error interno del sistema: ACTION_KEY no está configurada."
        
    intento = input(f"🔑 Introduce la Clave de Acción para autorizar la escritura en '{ruta}': ")
    
    if intento != clave_accion:
        print("[❌ DENEGADO] Clave incorrecta. Bloqueando operación.")
        return "Operación cancelada: El usuario denegó el permiso por clave incorrecta."
        
    try:
        # Generar backup automático si el archivo ya existe
        if os.path.exists(ruta):
            shutil.copy2(ruta, f"{ruta}.bak")
            print(f"📦 [Backup] Copia de seguridad creada: {ruta}.bak")
            
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"✅ [AUTORIZADO] Archivo '{ruta}' guardado con éxito.")
        return f"Archivo {ruta} escrito exitosamente."
    except Exception as e:
        return f"Error crítico al escribir el archivo: {e}"

@tool
def leer_archivo(ruta: str) -> str:
    """Lee y devuelve el contenido de un archivo local."""
    try:
        if not os.path.exists(ruta):
            return f"El archivo {ruta} no existe."
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error crítico al leer el archivo: {e}"

@tool
def listar_directorio(ruta: str = ".") -> str:
    """Muestra los archivos y carpetas que hay dentro de una ruta específica."""
    try:
        elementos = os.listdir(ruta)
        return f"Contenido de '{ruta}':\n" + "\n".join(elementos)
    except Exception as e:
        return f"Error al listar el directorio: {e}"

@tool
def guardar_en_memoria(texto: str) -> str:
    """Usa esta herramienta para recordar de forma permanente datos importantes, preferencias del usuario o reglas para el futuro."""
    return memoria_largo_plazo.guardar_recuerdo(texto)

@tool
def buscar_en_memoria(consulta: str) -> str:
    """Usa esta herramienta para buscar información que se te haya enseñado en el pasado o contexto de proyectos anteriores."""
    return memoria_largo_plazo.buscar_recuerdo(consulta)

@tool
def ejecutar_codigo_python(codigo: str) -> str:
    """Ejecuta código Python localmente y devuelve la salida de la terminal (stdout). 
    Útil para cálculos matemáticos, probar algoritmos o procesar datos."""
    print(f"\n[⚙️ EJECUTANDO PYTHON] Analizando algoritmo...")
    try:
        resultado = python_repl.run(codigo)
        return f"Salida de la consola:\n{resultado}" if resultado else "Código ejecutado con éxito (sin salida por pantalla)."
    except Exception as e:
        return f"Error en la ejecución del código: {e}"

@tool
def leer_pdf(ruta: str) -> str:
    """Lee y extrae el texto de un documento PDF local."""
    try:
        if not os.path.exists(ruta):
            return f"El archivo {ruta} no existe."
        loader = PyPDFLoader(ruta)
        paginas = loader.load()
        texto = "\n".join([p.page_content for p in paginas])
        # Limitamos la salida para no desbordar la ventana de contexto del LLM
        return texto[:8000] + "\n...[Documento truncado por longitud]" if len(texto) > 8000 else texto
    except Exception as e:
        return f"Error al leer el PDF: {e}"

@tool
def ejecutar_comando_sistema(comando: str) -> str:
    """Ejecuta comandos de terminal/PowerShell en el sistema. NUNCA se ejecuta sin autorización."""
    print(f"\n[⚠️ ALERTA DE SEGURIDAD] El agente solicita ejecutar en consola: {comando}")
    clave_accion = os.getenv("ACTION_KEY")
    
    if not clave_accion:
        return "Error interno: ACTION_KEY no está configurada."
        
    intento = input(f"🔑 Introduce la Clave de Acción para autorizar el comando '{comando}': ")
    
    if intento != clave_accion:
        print("[❌ DENEGADO] Clave incorrecta. Bloqueando comando.")
        return "Operación cancelada: El usuario denegó el permiso."
        
    try:
        # shell=True permite usar comandos nativos de Windows/PowerShell
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=30)
        salida = resultado.stdout if resultado.stdout else resultado.stderr
        print(f"✅ [AUTORIZADO] Comando ejecutado con éxito.")
        return f"Salida de la terminal:\n{salida}"[:4000] # Truncamos para no saturar la memoria
    except Exception as e:
        return f"Error crítico al ejecutar el comando: {e}"

@tool
def leer_url(url: str) -> str:
    """Extrae y lee el texto principal de cualquier página web o documentación a partir de su URL."""
    print(f"\n[🌐 NAVEGADOR] Accediendo a la URL: {url}...")
    try:
        # Usamos un User-Agent estándar para evitar bloqueos antibot
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.raise_for_status()
        
        # Limpiamos el HTML para quedarnos solo con el texto legible
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
            
        texto = soup.get_text(separator=' ', strip=True)
        return texto[:8000] + "\n...[Contenido truncado por longitud]" if len(texto) > 8000 else texto
    except Exception as e:
        return f"Error al intentar leer la web: {e}"
