import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Forzar conexión web estándar a nivel de sistema operativo
os.environ["GOOGLE_API_USE_REST"] = "true"

load_dotenv()
print("Iniciando prueba de conexión directa con LangChain...")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0)
    respuesta = llm.invoke("Escribe exactamente la palabra 'Funciona'")
    print(f"Respuesta del LLM: {respuesta.content}")
except Exception as e:
    print(f"Error: {e}")