import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.workflows.orchestrator import ejecutar_flujo_completo
from src.memory.short_term import GestorMemoria
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Inicializamos el motor gráfico
console = Console()
memoria = GestorMemoria()

console.print(Panel.fit(
    "[bold blue]⚡ ZEUS INICIADO[/bold blue]\n[green]Arquitectura Multi-Agente | Interfaz Enriquecida | Multihilo Activo[/green]\nEscribe 'salir' para apagar.", 
    border_style="cyan"
))

while True:
    entrada_usuario = console.input("\n[bold magenta]Tú:[/bold magenta] ")
    if entrada_usuario.lower() in ['salir', 'exit']:
        console.print("[bold red]Apagando orquestador...[/bold red]")
        break
    try:
        contexto_actual = memoria.obtener_contexto()
        
        # Ejecuta la cadena paralela
        resultado = ejecutar_flujo_completo(entrada_usuario, contexto_actual)
        memoria.agregar_interaccion(entrada_usuario, resultado)
        
        # Renderiza la salida unificada de todos los agentes en Markdown formateado
        console.print("\n[bold cyan]🤖 INFORME FINAL CONSOLIDADO:[/bold cyan]")
        console.print(Panel(Markdown(resultado), border_style="green"))
        
    except Exception as e:
        console.print(f"\n[bold red][ERROR GLOBAL]: {e}[/bold red]")