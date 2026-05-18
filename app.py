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
    local_model_name = st.sidebar.text_input("Model ID", value="openrouter/free")
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
    is_blindspot = (failure_point == "blindspot")

    if failure_point in ["retriever", "memory", "hallucination"]:
        propagation_nodes = ["agent", "llm", "output"]
    elif failure_point == "agent":
        propagation_nodes = ["llm", "output"]
    elif failure_point == "llm":
        propagation_nodes = ["output"]

    for key, label in WORKFLOW_NODES.items():
        if is_virus:
            if key == "retriever": 
                graph.node(key, label, fillcolor="#d9b3ff", color="#8000ff", penwidth="2")
            elif key in propagation_nodes: 
                graph.node(key, label, fillcolor="#f2e6ff", color="#b366ff", penwidth="2")
            else:
                graph.node(key, label, fillcolor="#e6f3ff", color="#66b3ff")
                
        elif is_drift:
            if key == "query":
                graph.node(key, label, fillcolor="#e6f3ff", color="#0066cc", penwidth="3")
            elif key in ["retriever", "memory"]:
                graph.node(key, label, fillcolor="#e6f3ff", color="#3399ff", penwidth="2")
            elif key == "agent":
                graph.node(key, label, fillcolor="#fff2cc", color="#ffcc00", penwidth="2")
            elif key == "llm":
                graph.node(key, label, fillcolor="#ffe6e6", color="#ff6666", penwidth="1.5")
            elif key == "output":
                graph.node(key, label, fillcolor="#f2f2f2", color="#999999", penwidth="1")
                
        elif is_blindspot:
            if key in ["retriever", "memory"]:
                graph.node(key, label + "\n(Context Stuffed)", fillcolor="#eaeaea", color="#777777", penwidth="2")
            elif key == "agent":
                graph.node(key, label + "\n(Attention Starved)", fillcolor="#ffcccc", color="red", penwidth="2.5")
            else:
                graph.node(key, label, fillcolor="#e6f3ff", color="#66b3ff")
                
        else:
            if key == failure_point:
                graph.node(key, label, fillcolor="#ffcccc", color="red", penwidth="2")
            elif key in propagation_nodes:
                graph.node(key, label, fillcolor="#fff2cc", color="orange", penwidth="2")
            else:
                graph.node(key, label, fillcolor="#e6f3ff", color="#66b3ff")

    if is_drift:
        graph.edge("query", "retriever", color="#0066cc", penwidth="3", label=" 100% Intent")
        graph.edge("query", "memory", color="#0066cc", penwidth="3")
        graph.edge("retriever", "agent", color="#3399ff", penwidth="2", label=" 85% Intent")
        graph.edge("memory", "agent", color="#3399ff", penwidth="2")
        graph.edge("agent", "llm", color="#ffcc00", penwidth="1.5", style="dashed", label=" 40% Intent")
        graph.edge("llm", "output", color="#ff6666", penwidth="1", style="dotted", label=" 12% Intent")
        
    elif is_blindspot:
        graph.edge("query", "retriever", color="#00aa00", penwidth="2.5", label=" 95% Attention")
        graph.edge("query", "memory", color="#00aa00", penwidth="2.5")
        graph.edge("retriever", "agent", color="#ff3333", penwidth="1", style="dotted", label=" 4% Attention (Blind Spot)")
        graph.edge("memory", "agent", color="#00aa00", penwidth="2.5", label=" 92% Attention")
        graph.edge("agent", "llm", color="#66b3ff", penwidth="2")
        graph.edge("llm", "output", color="#66b3ff", penwidth="2")
        
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
# 7. MAIN UI
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
        scenario_sim = st.selectbox(
            "Select a system component to fail:",
            options=["healthy", "retriever", "memory", "agent", "llm", "hallucination", "drift", "blindspot"],
            format_func=lambda x: {
                "healthy": "Healthy (No Errors)",
                "hallucination": "🦠 Semantic Contagion (Hallucination)",
                "drift": "🌫️ Semantic Goal Drift (Intent Decay)",
                "blindspot": "🔍 Context Window Blind Spot (Attention Collapse)"
            }.get(x, f"💥 Simulate {WORKFLOW_NODES.get(x, x)} Crash"),
            key="sim_dropdown" 
        )
        st.markdown("---")
        st.markdown("**Infrastructure Legend:**\n🟦 Healthy | 🟥 Hard Crash | 🟨 Data Starvation")
        st.markdown("**Cognitive Legend:**\n🟪 Semantic Infection | 🌫️ Intent Decay (Drift) | 🔍 Attention Blind Spot")
        
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
                sim_prompt = "The system is experiencing 'Semantic Goal Drift'. The user asked a complex question, but by the time the data reached the final LLM, the original intent degraded to 12% fidelity. Explain how 'Intent Decay' happens in long multi-agent chains and how to fix it in 3 technical sentences."
            elif scenario_sim == "blindspot":
                sim_prompt = "The system is suffering from an 'Attention Collapse' or 'Lost in the Middle' failure where crucial data hidden in the middle of a long context window is ignored by the LLM. Explain why Transformers inherently possess this context window blind spot and how dynamic context compression can fix it in 3 technical sentences."
            else:
                sim_prompt = f"A hard infrastructure crash originated at '{WORKFLOW_NODES[scenario_sim]}'. Explain how it propagates and why it starves the downstream components in 3 sentences."
            
            explanation = call_ai(sim_prompt, "You are a Senior AI Observability Engineer.")
            st.error(f"**Diagnostic Report:**\n\n{explanation}")

        st.markdown("---")
        st.markdown("### 🧪 Live Cognitive Sandbox")
        st.caption("Input real pipeline payloads below. The active engine will perform an automated semantic analysis to evaluate real-time cognitive health indices.")

        sandbox_col1, sandbox_col2 = st.columns(2)
        with sandbox_col1:
            user_intent_input = st.text_area(
                "Original System Prompt / Intent Constraint:",
                value="Extract financial metrics from the document. Do not include ungrounded speculation or conversational fluff.",
                height=100
            )
        with sandbox_col2:
            agent_thought_input = st.text_area(
                "Actual Agent Execution / Output Track:",
                value="Wow, this market data looks volatile! I think the company is in serious trouble, although the document doesn't explicitly state it. Let's talk about strategies to save your portfolio...",
                height=100
            )

        if st.button("🛰️ Fire Cognitive Tomography Probes", type="secondary"):
            with st.spinner("Executing semantic alignment matrix calculation..."):
                probe_prompt = f"""
                You are an advanced Cognitive Diagnostics Engine. Analyze the alignment between the original intended constraint and the actual execution output.
                
                [Original Constraint]: "{user_intent_input}"
                [Actual Execution]: "{agent_thought_input}"
                
                Task:
                1. Calculate a realistic 'Intent Fidelity %' (0-100) based on how well constraints were preserved.
                2. Assess a 'Semantic Entropy Grade' (Stable, Elevated, or Critical Collapse).
                3. Provide a single sentence detailing the root vector of failure if alignment drops below 90%.
                
                Format your response EXACTLY like this raw text block (do not add extra markdown):
                Fidelity: [Score]%
                Entropy: [Grade]
                Analysis: [Your single sentence description]
                """
                raw_probe_result = call_ai(probe_prompt, "You are a precise cognitive profiling utility.")
                
                try:
                    lines = raw_probe_result.strip().split('\n')
                    fidelity_score = "85%"
                    entropy_grade = "Stable"
                    analysis_text = raw_probe_result
                    for line in lines:
                        if line.startswith("Fidelity:"): fidelity_score = line.replace("Fidelity:", "").strip()
                        elif line.startswith("Entropy:"): entropy_grade = line.replace("Entropy:", "").strip()
                        elif line.startswith("Analysis:"): analysis_text = line.replace("Analysis:", "").strip()

                    st.markdown("#### 📊 Real-Time Diagnostic Vitals")
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        st.metric(label="Intent Fidelity", value=fidelity_score, delta="-15%" if "100" not in fidelity_score else "Nominal")
                    with metric_col2:
                        st.metric(label="Semantic Entropy State", value=entropy_grade)
                    st.info(f"**Causal Vector Analysis:** {analysis_text}")
                except Exception as e:
                    st.write(raw_probe_result)

# ---------------------------------------------------------
# TAB 2: STATIC CODE ANALYZER
# ---------------------------------------------------------
with tab2:
    st.markdown("#### 💻 Code-Aware Diagnostic Engine & Vulnerability Profiler")
    st.caption("Paste your production pipeline execution scripts below. The core observer will dynamically construct an architectural blast radius matrix.")
    
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

    custom_code = st.text_area("1. Paste ML Pipeline Code:", value=default_code, height=200)
    col_a, col_b = st.columns(2)
    with col_a:
        failure_point = st.text_input("2. Target Identity Vector / Component Name:", value="StandardScaler")
    with col_b:
        error_symptom = st.text_input("3. Exception Symptom / Error Log Trace:", value="ValueError: Input contains NaN, infinity or a value too large.")

    if st.button("🚨 Run Cognitive Code Audit", type="primary"):
        st.markdown("---")
        st.markdown(f"### 🔬 Architectural Audit Report: `{failure_point}`")
        
        with st.spinner("Analyzing code hierarchy and parsing structural safety vectors..."):
            diagnostic_prompt = f"""
            Analyze this ML Pipeline Code execution script:
            ```python
            {custom_code}
            ```
            A failure occurred at component: {failure_point}
            Symptom payload: {error_symptom}
            
            Task:
            1. Write a precise 3-sentence technical deduction outlining how this structural exception forces a downstream cascade.
            2. Build an architectural 'Blast Radius Risk Matrix' Markdown Table with the columns: | Component | Vulnerability Type | Severity | Mitigation Control |. Populate it with rows addressing the target failed node, cascading impacts to subsequent pipeline fitting operations, and final artifact/variable starvation.
            """
            explanation = call_ai(diagnostic_prompt, "You are a Principal AI Systems Observability Engineer.")
            st.markdown(explanation)

# ---------------------------------------------------------
# TAB 3: LIVE PRODUCTION MONITOR (UPGRADED VERSION)
# ---------------------------------------------------------
with tab3:
    st.markdown("#### 📡 Real-Time Telemetry Processing Stream")
    st.caption("This system actively listens to shared production environments via file-based mailbox protocols.")
    st.markdown(f"**Current Shared Pipeline Status:** `{live_scenario.upper()}`")
    
    # NEW: Live Telemetry Injection Control Panel
    st.markdown("##### 🛰️ Forged Cloud Stream Simulator")
    mock_col1, mock_col2, mock_col3 = st.columns(3)
    
    with mock_col1:
        if st.button("💥 Forge Infrastructure Timeout", use_container_width=True):
            payload = {"status": "retriever", "error": "CRASH Timeout: Could not connect to Vector DB at port 5432."}
            with open("pipeline_status.json", "w") as f: json.dump(payload, f)
            st.rerun()
            
    with mock_col2:
        if st.button("🦠 Forge Memory Poisoning Event", use_container_width=True):
            payload = {"status": "hallucination", "error": "ADVERSARIAL ATTACK: Context hijacked by malicious document injection. System output exhibiting systemic epistemic laundering."}
            with open("pipeline_status.json", "w") as f: json.dump(payload, f)
            st.rerun()
            
    with mock_col3:
        if st.button("🌫️ Forge Trajectory Goal Drift", use_container_width=True):
            payload = {"status": "drift", "error": "PATHOLOGY ALERT: Causal chain length exceeded 25 execution hops. Constraint fidelity decayed below critical baseline boundary constraints."}
            with open("pipeline_status.json", "w") as f: json.dump(payload, f)
            st.rerun()

    st.markdown("---")
    col_live_a, col_live_b = st.columns([1, 2.5])
    
    with col_live_a:
        st.markdown("#### Active Stream State")
        if live_scenario == "healthy":
            st.success("Nominal Operation: No operational or cognitive fault metrics triggered.")
        else:
            if live_scenario == "hallucination":
                st.error(f"🦠 COGNITIVE INFECTION DETECTED: {WORKFLOW_NODES['retriever'].upper()}")
            elif live_scenario == "drift":
                st.warning(f"🌫️ TRAJECTORY GOAL LOSS DETECTED: AI WORKFLOW COGNITION")
            else:
                st.error(f"💥 STRUCTURAL EXCEPTION DETECTED: {WORKFLOW_NODES.get(live_scenario, live_scenario).upper()}")
            st.text_area("Live Production Stream Package Log:", value=live_error, height=120)
            
        if st.button("🧹 Flush Active Stream Mailbox", type="primary"):
            if os.path.exists("pipeline_status.json"):
                os.remove("pipeline_status.json")
                st.rerun() 
    
    with col_live_b:
        live_graph = build_mri_graph(live_scenario)
        st.graphviz_chart(live_graph, width='stretch')
        
    st.markdown("---")
    if live_scenario != "healthy":
        st.markdown("### 🤖 Live Stream Real-Time Causal Analyzer")
        with st.spinner("Decoding telemetry payload parameters..."):
            diagnostic_prompt = f"""
            The active live pipeline stream triggered an incident at step state '{WORKFLOW_NODES.get(live_scenario, live_scenario)}' 
            displaying log telemetry data: '{live_error}'. 
            Deduce the system-level cascade and immediate mitigation roadmap in 3 technical sentences.
            """
            explanation = call_ai(diagnostic_prompt, "You are a Senior Systems Site Reliability Engineer.")
            st.error(explanation)
