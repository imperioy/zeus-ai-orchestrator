# ⚡ Zeus - Local AI Multi-Agent Orchestrator

Zeus is an advanced personal and local Artificial Intelligence agent for the terminal. It acts as a master orchestrator that breaks down complex requests, plans workflows, and launches multiple parallel agents (multithreading) using specialized tools. 

It is built with **Python**, **LangChain**, and **LangGraph**, utilizing a highly resilient architecture primarily powered by Google Gemini, with automatic fallback to local models (Ollama/Llama 3.1) as a backup.

## 🚀 Main Features

* **Concurrent Architecture (Multithreading):** Breaks down complex tasks and executes tools simultaneously without blocking using `ThreadPoolExecutor`.
* **High Availability (Self-Healing):** Automatic API key rotation and a fallback system to local models (Ollama) if the connection is lost or the quota is exhausted.
* **Vector Brain (Long-Term Memory):** Uses **ChromaDB** to remember the context of projects, conversations, or files across different sessions.
* **Strict Security:** Operating system command execution and file writing are protected by an administrator password (`ACTION_KEY`). Automatic generation of backup copies (`.bak`) when modifying code.
* **Tool Arsenal:**
  * 🌐 Full web browsing and Web Scraping (BeautifulSoup).
  * 🔍 Direct and intelligent information search (Wikipedia).
  * 🐍 Native Python interpreter for calculations and algorithms.
  * 💻 Execution of native terminal commands (PowerShell/Bash).
  * 📂 Local directory exploration and Document/PDF reading.
* **Rich Interface:** Visual console rendering powered by the `rich` library.

## 📋 Prerequisites

* **Python 3.11** or higher.
* A Google AI Studio (Gemini) API key.
* *(Optional)* **Ollama** installed locally with the `llama3.1` model downloaded, for the offline backup system.

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/imperioy/zeus-ai-orchestrator.git
   cd zeus-ai-orchestrator
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows:
   python -m venv venv
   .\venv\Scripts\activate
   
   # On Linux/macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Create a file named `.env` in the root of the project and configure your credentials. You must define a secret password (`ACTION_KEY`) that Zeus will ask for before executing critical actions on your computer:

```env
# Google API Keys
GEMINI_API_KEY1=your_primary_key_here
GEMINI_API_KEY2=your_secondary_key_here_optional

# Network restriction for the Google API
GOOGLE_API_USE_REST="true"

# Master security key to authorize terminal commands
ACTION_KEY=your_secret_password_here
```

## ⚡ Usage

To start the orchestrator, simply run:
```bash
python src/app/main.py
```

**(Optional) Set up Zeus as a global command on Windows:**
You can create a PowerShell alias to invoke Zeus from any directory on your computer by typing `zeus`. Add this to your PowerShell profile (`notepad $PROFILE`):

```powershell
function zeus {
    $OriginalDirectory = Get-Location
    Set-Location -Path "C:\Absolute\Path\To\Your\Zeus\Project"
    & ".\venv\Scripts\Activate.ps1"
    python src\app\main.py
    Set-Location -Path $OriginalDirectory
}
```

## ⚠️ Security Warning
This orchestrator has real permissions to read, write, and execute commands on the host system. Do not expose your `ACTION_KEY` or run Zeus on public servers without a controlled environment (sandbox or Docker). Use it at your own risk.