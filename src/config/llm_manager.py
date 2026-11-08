import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

os.environ["GOOGLE_API_USE_REST"] = "true"
load_dotenv()

def obtener_llm_robusto(modelo="gemini-1.5-flash", temperatura=0):
    # 1. Principal (Nube - Clave 1)
    llm_principal = ChatGoogleGenerativeAI(
        model=modelo, 
        temperature=temperatura,
        max_retries=0,
        google_api_key=os.getenv("GEMINI_API_KEY1")
    )
    
    # 2. Respaldo Nube (Clave 2)
    llm_respaldo = ChatGoogleGenerativeAI(
        model=modelo, 
        temperature=temperatura,
        max_retries=0,
        google_api_key=os.getenv("GEMINI_API_KEY2")
    )
    
    # 3. Respaldo Local (Ollama)
    llm_local = ChatOllama(model="llama3.1", temperature=temperatura)
    
    return llm_principal.with_fallbacks([llm_respaldo, llm_local])