# ==========================================
# 1. IMPORTS
# ==========================================
import streamlit as st
import graphviz
import requests
import google.generativeai as genai
import os    # <-- Added for reading the live telemetry file
import json  # <-- Added for reading the live telemetry file

# ==========================================
# 2. PAGE SETUP
# ==========================================
st.set_page_config(page_title="AI Workflow MRI", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 3. SIDEBAR (Universal AI Connection)
# ==========================================
st.sidebar.title("⚙️ Engine Settings")
ai_mode = st.sidebar.radio("Choose AI Backend:", ["Local / Custom Server", "Cloud AI (Gemini)"])
st.sidebar.markdown("---")

api_key = None
local_api_url = None
local_model_name = None
model = None

if ai_mode == "Local / Custom Server":
    st.sidebar.markdown("**📡 Custom Connection**")
    local_api_url = st.sidebar.text_input("API Endpoint URL", value="http://localhost:11434/v1/chat/completions")
    local_model_name = st.sidebar.text_input("Model Name", value="qwen2.5:3b")

elif ai_mode == "Cloud AI (Gemini)":
    st.sidebar.markdown("**☁️ Cloud Connection**")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
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

    # Define the blast radius / infection zone
    if failure_point in ["retriever", "memory", "hallucination"]:
        propagation_nodes = ["agent", "llm", "output"]
    elif failure_point == "agent":
        propagation_nodes = ["llm", "output"]
    elif failure_point == "llm":
        propagation_nodes = ["output"]

    for key, label in WORKFLOW_NODES.items():
        if is_virus:
            # 🦠 VIRUS MODE (Purple Semantic Drift)
            if key == "retriever": # Patient Zero
                graph.node(key, label, fillcolor="#d9b3ff", color="#8000ff", penwidth="2")
            elif key in propagation_nodes: # Infected Downstream
                graph.node(key, label, fillcolor="#f2e6ff", color="#b366ff", penwidth="2")
            else:
                graph.node(key, label, fillcolor="#e6f3ff", color="#66b3ff")
        else:
            # 💥 HARD CRASH MODE (Red/Orange)
            if key == failure_point:
                graph.node(key, label, fillcolor="#ffcccc", color="red", penwidth="2")
            elif key in propagation_nodes:
                graph.node(key, label, fillcolor="#fff2cc", color="orange", penwidth="2")
            else:
                graph.node(key, label, fillcolor="#e6f3ff", color="#66b3ff")

    # Draw the Edges (Connections)
    for start, end in EDGES:
        if is_virus and (start == "retriever" or start in propagation_nodes):
            # Dashed purple lines to show semantic infection spreading
            graph.edge(start, end, color="#8000ff", penwidth="2", style="dashed")
        elif start == failure_point or (start in propagation_nodes and end in propagation_nodes):
            # Solid red lines for hard failures
            graph.edge(start, end, color="red", penwidth="2")
        else:
            graph.edge(start, end, color="gray")
            
    return graph

# ==========================================
# 6. UNIVERSAL AI ENGINE
# ==========================================
def call_ai(prompt, system_prompt="You are a helpful AI assistant."):
    if ai_mode == "Local / Custom Server":
        try:
            data = {
                "model": local_model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            response = requests.post(local_api_url, headers={"Content-Type": "application/json"}, json=data)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return f"Server Error: {response.text}"
        except Exception as e:
            return f"Connection Failed. Details: {str(e)}"
            
    elif ai_mode == "Cloud AI (Gemini)":
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

# --- Upgraded Enterprise UI Tabs ---
tab1, tab2, tab3 = st.tabs([
    "🕹️ Interactive Simulator", 
    "💻 Static Code Analyzer",
    "📡 Live Production Monitor"
])

# ---------------------------------------------------------
# TAB 1: INTERACTIVE SIMULATOR (Manual Graph UI)
# ---------------------------------------------------------
with tab1:
    st.markdown("#### 🔬 Inject Failure & View Blast Radius")
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        # Added 'hallucination' to the options
        scenario_sim = st.selectbox(
            "Select a system component to fail:",
            options=["healthy", "retriever", "memory", "agent", "llm", "hallucination"],
            format_func=lambda x: "Healthy (No Errors)" if x == "healthy" else ("🦠 Semantic Contagion (Hallucination)" if x == "hallucination" else f"💥 Simulate {WORKFLOW_NODES[x]} Crash"),
            key="sim_dropdown" 
        )
        st.markdown("---")
        st.markdown("**Infrastructure Legend:**\n🟦 Healthy | 🟥 Hard Crash | 🟨 Data Starvation")
        st.markdown("**Cognitive Legend:**\n🟪 Patient Zero | 🪻 Semantic Infection")
        
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
            else:
                sim_prompt = f"A hard infrastructure crash originated at '{WORKFLOW_NODES[scenario_sim]}'. Explain how it propagates and why it starves the downstream components in 3 sentences."
            
            explanation = call_ai(sim_prompt, "You are a Senior AI Observability & Safety Engineer.")
            st.error(f"**Diagnostic Report:**\n\n{explanation}")

# ---------------------------------------------------------
# TAB 2: STATIC CODE ANALYZER
# ---------------------------------------------------------
with tab2:
    st.markdown("#### 💻 Code-Aware Diagnostic Engine")
    st.markdown("Paste your actual ML pipeline code (Python, PyTorch, Scikit-Learn). The AI will map the architecture directly from the code and diagnose failures.")
    
    default_code = """import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# 1. Ingest Data
data = pd.read_csv('user_data.csv')
X, y = data.drop('target', axis=1), data['target']

# 2. Define ML Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=100))
])

# 3. Execute Pipeline
pipeline.fit(X, y)
predictions = pipeline.predict(X)"""

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
            You are a Senior AI Observability Engineer and Static Code Analyzer.
            Analyze this ML Pipeline Code:
            ```python
            {custom_code}
            ```
            A critical failure occurred at: {failure_point}
            Error/Symptom: {error_symptom}
            Task:
            1. Identify how this specific failure disrupts the code execution path.
            2. Explain the "blast radius" (how it corrupts downstream variables like 'predictions' or subsequent models).
            3. Provide ONE highly specific, code-level recommendation to fix or catch this error before it crashes.
            Keep it highly technical, professional, and under 4 sentences.
            """
            explanation = call_ai(diagnostic_prompt, "You are an expert diagnostic AI and Python code analyzer.")
            st.error(explanation)

# ---------------------------------------------------------
# TAB 3: LIVE PRODUCTION MONITOR (Reads from pipeline.py)
# ---------------------------------------------------------
with tab3:
    st.markdown("#### 📡 Real-Time Script Monitoring")
    st.markdown("This tab is actively listening to your external `pipeline.py` script.")
    st.markdown(f"**Current Shared Pipeline Status:** `{live_scenario.upper()}`")
    
    col_live_a, col_live_b = st.columns([1, 2.5])
    
    with col_live_a:
        st.markdown("#### Status Details")
        if live_scenario == "healthy":
            st.success("All clear! No script errors detected.")
        else:
            st.error(f"CRASH DETECTED AT: {WORKFLOW_NODES[live_scenario].upper()}")
            st.text_area("Captured Error Log:", value=live_error, height=100)
            
        if st.button("🧹 Clear Live Error File"):
            if os.path.exists("pipeline_status.json"):
                os.remove("pipeline_status.json")
                st.rerun() # Refresh the page instantly
    
    with col_live_b:
        live_graph = build_mri_graph(live_scenario)
        st.graphviz_chart(live_graph, width='stretch')
        
    st.markdown("---")
    if live_scenario != "healthy":
        st.markdown("### 🤖 Automated Causal Diagnostic")
        with st.spinner("Analyzing live log data via local AI..."):
            diagnostic_prompt = f"""
            The live ML pipeline code just crashed at the '{WORKFLOW_NODES[live_scenario]}' step.
            The raw system error log is: "{live_error}"
            Write a brief, technical diagnostic report explaining how this specific crash corrupts downstream processes. 
            Keep it under 3 sentences.
            """
            explanation = call_ai(diagnostic_prompt, "You are an expert systems debugging assistant.")
            st.error(explanation)
