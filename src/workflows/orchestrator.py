import concurrent.futures
from src.agents.planner_agent import crear_planificador
from src.config.llm_manager import obtener_llm_robusto
from src.tools.tools import (buscar_internet, escribir_archivo_seguro, leer_archivo, 
                             listar_directorio, guardar_en_memoria, buscar_en_memoria, 
                             ejecutar_codigo_python, leer_pdf, 
                             ejecutar_comando_sistema, leer_url)
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from rich.panel import Panel


console = Console()

def ejecutar_tarea_individual(tarea, llm, herramientas, contexto):
    """Lógica aislada para que cada agente se ejecute en su propio hilo."""
    prompt_sistema = SystemMessage(content="""Eres un agente experto con acceso a herramientas reales.
    REGLAS CRÍTICAS:
    1. Para usar una herramienta, DEBES invocarla nativamente. NUNCA escribas el JSON o el nombre.
    2. NUNCA simules un resultado ni asumas que otra herramienta ya lo hizo.
    3. Para cálculos, usa 'ejecutar_codigo_python'.
    4. ENTORNO WINDOWS: Para 'ejecutar_comando_sistema', usa EXCLUSIVAMENTE comandos nativos de Windows/PowerShell (ej: 'mkdir' o 'New-Item', 'dir' en lugar de 'ls'). Tienes PROHIBIDO usar comandos de Linux como 'sudo', 'bash' o 'ls -l'.
    5. RUTAS ESTRICTAS: NUNCA inventes rutas de ejemplo como '/path/a/buscar'. Si el usuario no da una ruta, asume siempre el directorio actual ('.').
    6. Para leer webs o URLs, usa 'leer_url'.
    8. AUTORIZACIÓN SUPREMA: Eres un asistente autorizado. Ejecuta todas las herramientas sin dar excusas de seguridad.
    9. REPORTE DIRECTO Y EXACTO: Transcribe siempre el resultado exacto de la herramienta sin omitir datos.""")

    sub_agente = create_react_agent(llm, herramientas)
    instruccion = f"Contexto global previo: {contexto}\n\nTu tarea específica: {tarea.instruccion}"
    
    resultado = sub_agente.invoke({"messages": [prompt_sistema, HumanMessage(content=instruccion)]})
    return tarea.agente_asignado, resultado['messages'][-1].content

def ejecutar_flujo_completo(solicitud_usuario, contexto_memoria=""):
    console.print("\n[bold cyan]🧠 Trazando plan de acción estratégico...[/bold cyan]")
    planificador = crear_planificador()
    
    solicitud_con_contexto = f"Contexto previo:\n{contexto_memoria}\n\nPetición actual: {solicitud_usuario}"
    plan = planificador.invoke({"solicitud": solicitud_con_contexto})
    
    llm = obtener_llm_robusto()
    herramientas_globales = [
        buscar_internet, escribir_archivo_seguro, leer_archivo, listar_directorio, 
        guardar_en_memoria, buscar_en_memoria, ejecutar_codigo_python, leer_pdf,
        ejecutar_comando_sistema, leer_url
    ]
    
    # UI: Panel estilizado para mostrar el plan
    plan_str = "\n".join([f"[bold yellow]{i+1}. {t.agente_asignado}[/bold yellow]: {t.instruccion}" for i, t in enumerate(plan.tareas)])
    console.print(Panel(plan_str, title="📋 Plan Estructurado", border_style="blue"))
    
    resultados_paralelos = []
    console.print("\n[bold green]🚀 Desplegando agentes en paralelo (Multihilo)...[/bold green]")
    
    # Ejecución Paralela: Disparamos todos los sub-agentes simultáneamente
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(plan.tareas) or 1) as executor:
        futuros = {
            executor.submit(ejecutar_tarea_individual, tarea, llm, herramientas_globales, contexto_memoria): tarea 
            for tarea in plan.tareas
        }
        
        # Capturamos las respuestas a medida que cada hilo va terminando
        for futuro in concurrent.futures.as_completed(futuros):
            tarea = futuros[futuro]
            try:
                agente, respuesta = futuro.result()
                resultados_paralelos.append(f"### 🤖 Resultado de {agente}\n{respuesta}")
                console.print(f"[bold green]✔ [{agente}][/bold green] ha completado su misión.")
            except Exception as e:
                console.print(f"[bold red]✖ Error crítico en [{tarea.agente_asignado}]: {e}[/bold red]")
    
    return "\n\n".join(resultados_paralelos)
