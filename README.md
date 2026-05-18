# 🧠 AI Workflow MRI
**Causal Observability & Diagnostic Engine for Complex ML Pipelines**

Traditional observability tools give developers dashboards of raw metrics and stack traces, leaving them to manually trace the root cause. **AI Workflow MRI** is an automated diagnostic engine that acts as an "X-Ray" for machine learning pipelines. 

It intercepts live runtime errors, visually maps the downstream "blast radius", and uses Local AI to generate highly technical causal reports—all without exposing proprietary enterprise code to public cloud APIs.

## 🚀 Key Features

* **📡 Live Production Monitor:** Connects to external Python scripts via file-based telemetry to intercept runtime errors instantly.
* **💻 Static Code Analyzer:** Reads raw ML pipeline code (Scikit-Learn, PyTorch, Pandas), maps the architecture dynamically, and diagnoses variable-level failures.
* **🕹️ Interactive Simulator:** A visual sandbox to inject failures into a standard RAG (Retrieval-Augmented Generation) architecture and trace downstream corruption.
* **🔒 Privacy-First Local AI:** Engineered to run offline using local open-source models (via Ollama) to ensure zero data leakage for secure enterprise environments. Cloud fallback (Gemini) is also supported.

## 🏗️ Architecture & Telemetry
This project demonstrates a decoupled telemetry architecture. 
* **The Worker (`pipeline.py`):** The actual ML script executing data operations. If it crashes, it catches the exception and drops a JSON payload.
* **The Mailbox (`pipeline_status.json`):** The shared state file acting as a secure, local message broker.
* **The Dashboard (`app.py`):** The Streamlit UI that polls the mailbox, updates the visual Graphviz nodes, and routes the context to the local LLM for causal analysis.

## 🛠️ Tech Stack
* **Frontend:** Streamlit, Graphviz
* **Backend:** Python, JSON Telemetry
* **AI Engine:** Universal API router supporting Local AI (Ollama/Qwen) and Cloud AI (Google Gemini)

---

## 🏃‍♂️ How to Run Locally

### 1. Prerequisites
* Install [Python 3.8+](https://www.python.org/)
* Install [Ollama](https://ollama.com/) (For local AI diagnostics)
* Pull the default model via terminal: `ollama run qwen2.5:3b`

### 2. Installation
Clone the repository and install the required Python libraries:
```bash
git clone [https://github.com/bhavesh576/ai-workflow-mri.git](https://github.com/bhavesh576/ai-workflow-mri.git)
cd ai-workflow-mri
pip install -r requirements.txt
