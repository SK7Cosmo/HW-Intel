# HW Intel

**HW Intel** is a modern, re-engineered alternative to CPU-Z designed to extract and display system hardware diagnostics—including CPU specifications, memory metrics, and GPU details—with enhanced capabilities.

The project leverages automated software reverse engineering (SRE) pipelines and agentic AI workflows to analyze, decompile, and reconstruct low-level hardware detection utilities into a modernized application stack.

---

## 🛠️ Reengineering Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Runtime Environment** | Java Development Kit (JDK) | Required execution environment for Ghidra’s reverse engineering framework. |
| **Static Analysis & Decompilation** | Ghidra | Handles binary disassembling, decompiling, and static code analysis. |
| **Orchestration Layer** | REA (*Reengineer Anything*) | Model Context Protocol (MCP) server bridging the AI coding agent with Ghidra's API. |
| **Agentic AI Stack** | **Coding Agent:** Antigravity<br>**LLM:** Claude Sonnet 4.6| Automated reasoning, refactoring, and code generation driven by advanced language models. |

---

## 🚀 Getting Started

Follow these steps to run the backend service locally:

### Prerequisites

* Python 3.9+
* JDK (Java Development Kit) installed and configured in system path
* Ghidra installed and configured as System variable `[GHIDRA_HOME]`
* Virtual environment with dependencies installed

### Running the Application

Open PowerShell and execute the following commands:

```powershell
# Navigate to the backend directory
"Set-Location ".\HW Intel\backend""

# Start the Uvicorn ASGI server
python -m uvicorn main:app --host 127.0.0.1 --port 7890 --reload
```

Once the server starts successfully, access the web interface or API documentation by visiting:

👉 **[http://127.0.0.1:7890](http://127.0.0.1:7890)**

---
