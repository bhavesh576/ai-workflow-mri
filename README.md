# 🧠 AI Workflow MRI

## Causal Observability & Diagnostic Engine for Complex ML Pipelines

Traditional observability tools give developers dashboards of raw metrics and stack traces, leaving them to manually trace the root cause. **AI Workflow MRI** is an automated diagnostic engine that acts as an **"MRI" for machine learning pipelines**.

It intercepts live runtime errors, visually maps downstream **blast radius propagation**, and uses Local or Cloud AI to generate highly technical causal reports — while exposing hidden cognitive failure states that conventional observability platforms completely ignore.

---

# 🌐 Live Deployment

https://ai-workflow-mri-46vv9wjuftbkzon9kij64b.streamlit.app/

---

# 🚀 Key Advanced Features

## 📡 Live Production Monitor

Connects to external Python scripts via file-based telemetry to intercept runtime failures instantly and dynamically decode execution cascades.

---

## 💻 Static Code & Workspace Analyzer (SAST)

Reads raw ML pipeline code blocks or accepts whole-directory project uploads (`.py`, `.json`), parsing cross-file safety dependencies to build an interactive **Architectural Risk Matrix**.

---

## 🕹️ Interactive Cognitive Simulator

An advanced visual sandbox designed to inject both infrastructure failures and frontier cognitive pathologies:

### 🦠 Semantic Contagion (Hallucination Tracking)

Traces how a single corrupted document or false fact retrieved by a Vector DB silently propagates downstream, infecting reasoning agents through epistemic laundering.

### 🌫️ Semantic Goal Drift (Intent Decay)

Visualizes degradation of constraint adherence over long multi-agent loops where original user directives fade across cascading reasoning hops.

### 🔍 Context Window Blind Spot (Attention Collapse)

Maps transformer-level *Lost in the Middle* anomalies, highlighting pathways where oversized context windows starve critical information streams.

---

## 🧪 Live Cognitive Sandbox

Operational experimentation bay that evaluates live text interactions against system prompts to dynamically estimate:

* Intent Fidelity %
* Semantic Entropy States
* Context Integrity
* Reasoning Stability

---

## 🔒 Model-Agnostic Engine Router

Engineered with a universal backend routing layer supporting:

* OpenRouter
* OpenAI APIs
* Google Gemini
* Ollama local inference
* Enterprise local clusters
* Open-source LLM pipelines

---

# 🧠 Frontier Research Concepts

AI Workflow MRI explores emerging cognitive observability problems that traditional monitoring systems cannot detect:

* Semantic corruption propagation
* Hallucination root-cause tracing
* AI reasoning instability
* Multi-agent intent drift
* Context poisoning
* Retrieval corruption
* Cognitive workflow degradation
* Semantic entropy accumulation
* Long-chain reasoning collapse
* AI trustworthiness diagnostics

The project attempts to treat AI systems not merely as software pipelines — but as evolving cognitive systems requiring semantic-level observability.

---

# 🏗️ Architecture & Telemetry

This project demonstrates a decoupled telemetry architecture:

## ⚙️ The Worker (`pipeline.py`)

The actual ML script executing data operations. If it crashes, it catches exceptions and emits structured JSON telemetry payloads.

---

## 📬 The Mailbox (`pipeline_status.json`)

A shared local telemetry layer acting as a lightweight secure message broker between workflow execution and observability systems.

---

## 🖥️ The Dashboard (`app.py`)

The Streamlit observability interface that:

* polls telemetry continuously
* updates Graphviz workflow nodes
* visualizes blast radius propagation
* routes context into AI diagnostic engines
* generates semantic causal analysis

---

# 🛠️ Tech Stack

## Frontend

* Streamlit
* Graphviz

## Backend

* Python
* JSON Telemetry

## AI Systems

* Ollama
* Qwen
* OpenAI-compatible APIs
* Gemini APIs
* OpenRouter support

---

# 🏃‍♂️ How to Run Locally

## 1️⃣ Prerequisites

Install:

* Python 3.8+
* Ollama (for local AI diagnostics)

Download Ollama:
https://ollama.com/

Pull the default local model:

```bash
ollama run qwen2.5:3b
```

# 2️⃣ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/bhavesh576/ai-workflow-mri.git
cd ai-workflow-mri
pip install -r requirements.txt
```

# 3️⃣ Launch the Observability Hub

Start the Streamlit application:

```bash
streamlit run app.py
```

---

# 4️⃣ Engine Configuration

By default, the platform boots with a pre-configured cloud inference endpoint.

To enable privacy-first offline local AI execution:

## Step 1

Start Ollama locally.

## Step 2

Pull and run your preferred local model:

```bash
ollama run qwen2.5:3b
```

## Step 3

Inside the Streamlit sidebar configuration:

Set:

```txt
API Endpoint URL:
http://localhost:11434/v1/chat/completions
```

Clear:

```txt
API Key:
(empty)
```

This fully decouples the system from external cloud inference providers and enables local cognitive diagnostics.

---

# 🔬 Conceptual Vision

AI Workflow MRI is designed around a future-facing question:

> “How do we observe hidden semantic and cognitive failures inside intelligent systems?”

Rather than focusing only on infrastructure metrics, the platform experiments with cognitive observability concepts such as:

* reasoning integrity
* semantic corruption
* hallucination propagation
* intent decay
* cognitive drift
* hidden workflow degradation

The long-term vision is to evolve toward:

## “Cognitive Observability for Artificial Intelligence Systems”

A future where AI systems are debugged not only as software pipelines — but as complex reasoning ecosystems.

---

# ⚠️ Current Status

This project is currently a progressive research-style prototype built for:

* AI systems engineering exploration
* observability experimentation
* semantic failure analysis
* cognitive debugging research
* recruiter-facing innovation demos
* advanced portfolio development

---

# 👨‍💻 Developer

Bhavesh Tarale

GitHub:
https://github.com/bhavesh576

---

# 📌 Future Directions

Planned experimental directions include:

* hallucination origin tracing
* semantic blast-radius mapping
* multi-agent corruption analysis
* cognitive dependency graphs
* trustworthiness scoring
* semantic entropy tracking
* AI debate observability
* autonomous remediation systems
* reasoning lineage visualization
* cognitive black-box replay systems

---

# 🧩 Core Philosophy

Traditional observability platforms monitor systems.

AI Workflow MRI attempts to monitor cognition itself.
