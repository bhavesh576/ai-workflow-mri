# 🧠 AI Workflow MRI

**Visualizing Hidden Failures in Complex AI Systems**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-red?style=for-the-badge&logo=streamlit)](https://ai-workflow-mri-46vv9wjuftbkzon9kij64b.streamlit.app/)

**🌐 Access the Live Application Here:** [AI Workflow MRI Streamlit App](https://ai-workflow-mri-46vv9wjuftbkzon9kij64b.streamlit.app/)

AI Workflow MRI is a diagnostic and observability tool built with Streamlit. It helps AI engineers, site reliability engineers (SREs), and developers visualize, simulate, and diagnose failures in complex multi-agent LLM pipelines. Whether you are dealing with hard infrastructure crashes, semantic hallucinations, or context-window blind spots, this tool maps the "blast radius" and provides automated root-cause analysis.

---

## ✨ Key Features

* **🕹️ Interactive Simulator**: Inject simulated failures into a standard AI pipeline DAG (Directed Acyclic Graph) to visualize how errors propagate. Simulates structural crashes, semantic contagion (hallucinations), intent decay (drift), and attention collapse (blind spots).
* **🧪 Live Cognitive Sandbox**: Input real prompts and agent outputs to calculate real-time "Intent Fidelity" and "Semantic Entropy" scores.
* **💻 Static Code Analyzer**: Paste individual scripts or upload whole project directories (via `.py` and `.json` files) to generate an architectural Blast Radius Risk Matrix using LLM-powered code auditing.
* **📡 Live Production Monitor**: A file-based telemetry listener (`pipeline_status.json`) that monitors shared production environments and dynamically maps the health of active streams.
* **🔌 Universal AI Engine Support**:
    * **Native Google Gemini**: Connect directly using your Gemini API key.
    * **Universal Connection**: Works with Cloud API providers like OpenRouter and OpenAI, or local instances like Ollama and LM Studio.

---

## 📂 Project Structure

```text
ai-workflow-mri/
├── app.py                   # Main Streamlit application
├── pipeline.py              # Mock/External pipeline execution script
├── pipeline_status.json     # Telemetry mailbox for the Live Monitor
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.8+ installed. You will also need system-level support for Graphviz to render the pipeline charts.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/bhavesh576/ai-workflow-mri.git](https://github.com/bhavesh576/ai-workflow-mri.git)
   cd ai-workflow-mri
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure your `requirements.txt` includes `streamlit`, `graphviz`, `requests`, and `google-generativeai`)*

3. **Install System-level Graphviz:**
   * **Windows:** Download and install from [Graphviz Downloads](https://graphviz.org/download/) (ensure it's added to your system PATH).
   * **macOS:** `brew install graphviz`
   * **Linux (Ubuntu/Debian):** `sudo apt-get install graphviz`

### Running the App Locally

Start the Streamlit server:
```bash
streamlit run app.py
```
The app will automatically open in your default web browser at `http://localhost:8501`.

---

## ⚙️ Configuration & Usage

Once the app is running, use the **⚙️ Engine Settings** sidebar to configure your AI Backend:

### Option A: Google Gemini
1. Select "Google Gemini" as the AI Backend.
2. Input your Gemini API Key (Starts with `AIza...`).

### Option B: Universal (Local / OpenRouter / Cloud)
1. Select "Universal Connection".
2. **For OpenRouter (Cloud):** Use the default endpoint `https://openrouter.ai/api/v1/chat/completions`, choose your Model ID (e.g., `openrouter/free`), and input your API key.
3. **For Local (Ollama/LM Studio):** Point the API Endpoint URL to your local host (e.g., `http://localhost:11434/v1/chat/completions`), specify the local model name, and leave the API key blank or type a dummy key if required.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

---

## 📝 License

This project is open-source and available under the MIT License.
