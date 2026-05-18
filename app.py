# ==========================================
# 1. IMPORTS
# ==========================================
import streamlit as st
import graphviz
import requests
import google.generativeai as genai
import os
import json

# ==========================================
# 2. PAGE SETUP
# ==========================================
st.set_page_config(page_title="AI Workflow MRI", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 3. SIDEBAR (Universal AI Connection)
# ==========================================
st.sidebar.title("⚙️ Engine Settings")

ai_mode = st.sidebar.radio("Choose AI Backend:", ["Universal (Local / OpenRouter / Cloud)", "Google Gemini"])
st.sidebar.markdown("---")

api_key = None
local_api_url = None
local_model_name = None
custom_api_key = None
model = None

if ai_mode == "Universal (Local / OpenRouter / Cloud)":
    st.sidebar.markdown("**🌐 Universal Connection**")
    st.sidebar.caption("Works with Ollama, LM Studio, OpenRouter, OpenAI, etc.")
    
    local_api_url = st.sidebar.text_input("API Endpoint URL", value="http://localhost:11434/v1/chat/completions")
    local_model_name = st.sidebar.text_input("Model ID", value="qwen2.5:3b")
    custom_api_key = st.sidebar.text_input("API Key (Leave blank for local)", type="password")

elif ai_mode == "Google Gemini":
    st.sidebar.markdown("**☁️ Native Google Connection**")
    api_key = st.sidebar.text_input("Gemini API Key (Starts with AIza...)", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

# ==========================================
# 4. WORKFLOW DATA
# ==========================================
WORKFLOW_NODES = {
    "query": "User Query",
    "retriever": "Retriever (Vector DB)",
    "memory": "Context Memory",
    "agent": "Reasoning Agent",
    "llm": "Language Model (LLM)",
    "output": "Final Output"
}

EDGES = [
    ("query", "retriever"), ("query", "memory"),
    ("retriever", "agent"), ("memory", "agent"),
    ("agent", "llm"), ("llm", "output")
]

# ==========================================
# 5. GRAPH LOGIC
# ==========================================
def build_mri_graph(failure_point):
    graph = graphviz.Digraph(node_attr={'shape': 'box', 'style': 'filled,rounded', 'fontname': 'Helvetica'})
    graph.attr(rankdir='LR', bgcolor='transparent') 

    propagation_nodes = []
    is_virus = (failure_point == "hallucination")
    is_drift = (failure_point == "drift")

    if failure_point in ["retriever", "memory", "hallucination"]:
        propagation_nodes = ["agent", "llm", "output"]
    elif failure_point == "agent":
        propagation_nodes = ["llm", "output"]
    elif failure_point == "llm":
        propagation_nodes = ["output"]

    for key, label in WORKFLOW_NODES.items():
        if is_virus:
            # 🦠 VIRUS MODE (Purple Semantic Infection)
            if key == "retriever": 
                graph.node(key, label, fillcolor="#d9b3ff", color="#8000ff", penwidth="2")
            elif key in propagation_nodes: 
                graph.node(key, label, fillcolor="#f2e6ff", color="#b366ff", penwidth="2")
            else:
                graph.node(key, label, fillcolor="#e6f3ff", color="#66b3ff")
                
        elif is_drift:
            # 🌫️ DRIFT MODE (Fading Intent Fidelity)
            if key == "query":
                graph.node(key, label, fillcolor="#e6f3ff", color="#0066cc", penwidth="3") # Strong
            elif key in ["retriever", "memory"]:
                graph.node(key, label, fillcolor="#e6f3ff", color="#3399ff", penwidth="2") # Good
            elif key == "agent":
                graph.node(key, label, fillcolor="#fff2cc", color="#ffcc00", penwidth="2") # Drifting
            elif key == "llm":
                graph.node(key, label, fillcolor="#ffe6e6", color="#ff6666", penwidth="1.5") # Severely drifting
            elif key == "output":
                graph.node(key, label, fillcolor="#f2f2f2", color="#999999", penwidth="1") # Completely lost
                
        else:
            # 💥 HARD CRASH MODE (Red/Orange)
            if key == failure_point:
                graph.node(key, label, fillcolor="#ffcccc", color="red", penwidth="2")
            elif key in propagation_nodes:
                graph.node(key, label, fillcolor="#fff2cc", color="orange", penwidth="2")
            else:
                graph.node(key, label, fillcolor="#e6f3ff", color="#66b3ff")

    # Draw the Edges (Connections)
    if is_drift:
        # Custom edges showing the exact moment the goal gets lost
        graph.edge("query", "retriever", color="#0066cc", penwidth="3", label=" 100% Intent")
        graph.edge("query", "memory", color="#0066cc", penwidth="3")
        graph.edge("retriever", "agent", color="#3399ff", penwidth="2", label=" 85% Intent")
        graph.edge("memory", "agent", color="#3399ff", penwidth="2")
        graph.edge("agent", "llm", color="#ffcc00", penwidth="1.5", style="dashed", label=" 40% Intent")
        graph.edge("llm", "output", color="#ff6666", penwidth="1", style="dotted", label=" 12% Intent")
    else:
        for start, end in EDGES:
            if is_virus and (start == "retriever" or start in propagation_nodes):
                graph.edge(start, end, color="#8000ff", penwidth="2", style="dashed")
            elif start == failure_point or (start in propagation_nodes and end in propagation_nodes):
                graph.edge(start, end, color="red", penwidth="2")
            else:
                graph.edge(start, end, color="gray")
            
    return graph
# ==========================================
# 6. UNIVERSAL AI ENGINE
# ==========================================
def call_ai(prompt, system_prompt="You are a helpful AI assistant."):
    if ai_mode == "Universal (Local / OpenRouter / Cloud)":
        try:
            headers = {"Content-Type": "application/json"}
            
            if custom_api_key:
                headers["Authorization"] = f"Bearer {custom_api_key}"
                headers["HTTP-Referer"] = "https://github.com/bhavesh576/ai-workflow-mri"
                headers["X-Title"] = "AI Workflow MRI"
            
            data = {
                "model": local_model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            response = requests.post(local_api_url, headers=headers, json=data)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return f"Server Error {response.status_code}: {response.text}"
            
        except Exception as e:
            return f"Connection Failed. Details: {str(e)}"
            
    elif ai_mode == "Google Gemini":
        if not api_key: return "⚠️ Please enter your Gemini API key."
        try:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            return model.generate_content(full_prompt).text
        except Exception as e:
            return f"API Error: {str(e)}"

# ==========================================
# LIVE TELEMETRY CHECKER (Background Logic)
# ==========================================
if os.path.exists("pipeline_status.json"):
    with open("pipeline_status.json", "r") as f:
        live_data = json.load(f)
    live_scenario = live_data["status"]
    live_error = live_data["error"]
else:
    live_scenario = "healthy"
    live_error = "No external error logs found."

# ==========================================
# 7. MAIN UI WITH 3 TABS
# ==========================================
st.title("🧠 AI Workflow MRI")
st.markdown("### Visualizing Hidden Failures in Complex AI Systems")

tab1, tab2, tab3 = st.tabs([
    "🕹️ Interactive Simulator", 
    "💻 Static Code Analyzer",
    "📡 Live Production Monitor"
])

# ---------------------------------------------------------
# TAB 1: INTERACTIVE SIMULATOR
# ---------------------------------------------------------
with tab1:
    st.markdown("#### 🔬 Inject Failure & View Blast Radius")
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        # Added 'drift' to the options list
        scenario_sim = st.selectbox(
            "Select a system component to fail:",
            options=["healthy", "retriever", "memory", "agent", "llm", "hallucination", "drift"],
            format_func=lambda x: {
                "healthy": "Healthy (No Errors)",
                "hallucination": "🦠 Semantic Contagion (Hallucination)",
                "drift": "🌫️ Semantic Goal Drift (Intent Decay)"
            }.get(x, f"💥 Simulate {WORKFLOW_NODES.get(x, x)} Crash"),
            key="sim_dropdown" 
        )
        st.markdown("---")
        st.markdown("**Infrastructure Legend:**\n🟦 Healthy | 🟥 Hard Crash | 🟨 Data Starvation")
        st.markdown("**Cognitive Legend:**\n🟪 Semantic Infection | 🌫️ Intent Decay (Drift)")
        
    with col2:
        mri_graph = build_mri_graph(scenario_sim)
        st.graphviz_chart(mri_graph, width='stretch')

    st.markdown("---")
    if scenario_sim == "healthy":
        st.success("**Status:** System is operating nominally.")
    else:
        with st.spinner(f"Generating MRI Diagnostic Report..."):
            if scenario_sim == "hallucination":
                sim_prompt = "A False Fact (Hallucination) was retrieved by the Vector DB. Explain the concept of 'Epistemic Laundering' and how this false fact invisibly infects the downstream reasoning agents and final LLM output in 3 technical sentences."
            elif scenario_sim == "drift":
                # NEW PROMPT for the drift scenario
                sim_prompt = "The system is experiencing 'Semantic Goal Drift'. The user asked a complex question, but by the time the data reached the final LLM, the original intent degraded to 12% fidelity. Explain how 'Intent Decay' happens in long multi-agent chains and how to fix it in 3 technical sentences."
            else:
                sim_prompt = f"A hard infrastructure crash originated at '{WORKFLOW_NODES[scenario_sim]}'. Explain how it propagates and why it starves the downstream components in 3 sentences."
            
            explanation = call_ai(sim_prompt, "You are a Senior AI Observability Engineer.")
            st.error(f"**Diagnostic Report:**\n\n{explanation}")

# ---------------------------------------------------------
# TAB 2: STATIC CODE ANALYZER
# ---------------------------------------------------------
with tab2:
    st.markdown("#### 💻 Code-Aware Diagnostic Engine")
    default_code = """import pandas as pd\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.ensemble import RandomForestClassifier\n\n# 1. Ingest Data\ndata = pd.read_csv('user_data.csv')\nX, y = data.drop('target', axis=1), data['target']\n\n# 2. Define ML Pipeline\npipeline = Pipeline([\n    ('scaler', StandardScaler()),\n    ('classifier', RandomForestClassifier(n_estimators=100))\n])\n\n# 3. Execute Pipeline\npipeline.fit(X, y)\npredictions = pipeline.predict(X)"""
    custom_code = st.text_area("1. Paste ML Pipeline Code:", value=default_code, height=250)
    col_a, col_b = st.columns(2)
    with col_a:
        failure_point = st.text_input("2. Which component/variable crashed?", value="StandardScaler")
    with col_b:
        error_symptom = st.text_input("3. (Optional) Paste an error log:", value="ValueError: Input contains NaN, infinity or a value too large.")

    if st.button("🚨 Run Code-Level Diagnostic", type="primary"):
        st.markdown("---")
        st.markdown(f"### 🔬 Diagnostic Report: `{failure_point}`")
        with st.spinner("Analyzing code structure and mapping blast radius..."):
            diagnostic_prompt = f"""
            Analyze this ML Pipeline Code:
            ```python
            {custom_code}
            ```
            A critical failure occurred at: {failure_point}
            Error/Symptom: {error_symptom}
            Task: 
            1. Identify how this specific failure disrupts the code execution path. 
            2. Explain the blast radius. 
            3. Provide ONE highly specific code-level fix. 
            Keep it under 4 sentences.
            """
            explanation = call_ai(diagnostic_prompt, "You are an expert Python code analyzer.")
            st.error(explanation)

# ---------------------------------------------------------
# TAB 3: LIVE PRODUCTION MONITOR
# ---------------------------------------------------------
with tab3:
    st.markdown("#### 📡 Real-Time Script Monitoring")
    st.markdown(f"**Current Shared Pipeline Status:** `{live_scenario.upper()}`")
    col_live_a, col_live_b = st.columns([1, 2.5])
    
    with col_live_a:
        st.markdown("#### Status Details")
        if live_scenario == "healthy":
            st.success("All clear! No script errors detected.")
        else:
            if live_scenario == "hallucination":
                st.error(f"🦠 COGNITIVE INFECTION DETECTED: {WORKFLOW_NODES['retriever'].upper()}")
            else:
                st.error(f"💥 CRASH DETECTED AT: {WORKFLOW_NODES.get(live_scenario, live_scenario).upper()}")
            st.text_area("Captured Error Log / Symptom:", value=live_error, height=100)
            
        if st.button("🧹 Clear Live Error File"):
            if os.path.exists("pipeline_status.json"):
                os.remove("pipeline_status.json")
                st.rerun() 
    
    with col_live_b:
        live_graph = build_mri_graph(live_scenario)
        st.graphviz_chart(live_graph, width='stretch')
        
    st.markdown("---")
    if live_scenario != "healthy":
        st.markdown("### 🤖 Automated Causal Diagnostic")
        with st.spinner("Analyzing live log data via AI..."):
            diagnostic_prompt = f"""
            The live ML pipeline script experienced an event at '{WORKFLOW_NODES.get(live_scenario, live_scenario)}' 
            with the log/symptom: '{live_error}'. 
            Explain the downstream blast radius in 3 sentences.
            """
            explanation = call_ai(diagnostic_prompt, "You are an expert systems debugging assistant.")
            st.error(explanation)
