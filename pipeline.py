import json
import time

def run_my_real_ml_pipeline():
    # 1. At the start, assume everything is healthy and write it to the JSON file
    state = {"status": "healthy", "error": ""}
    with open("pipeline_status.json", "w") as f:
        json.dump(state, f)
        
    print("🚀 ML Pipeline Started...")
    time.sleep(2) # Simulating data loading...

    try:
        # 2. Simulate connecting to the next steps
        print("🔍 Connecting to Vector Database (Retriever)... Success!")
        time.sleep(1)
        
        print("🧠 Reasoning Agent starting calculations...")
        time.sleep(1)
        
        # --- SIMULATE CRASH ---
        # Force a real Runtime Error (Dividing by zero) inside the Agent
        bad_math = 100 / 0 
        
    except Exception as e:
        # 3. Catch the error and write it to the shared JSON file
        print(f"💥 CRASH DETECTED: {type(e).__name__} - {str(e)}")
        
        # Notice we changed the status to 'agent' here!
        state = {"status": "agent", "error": f"Math/Logic Error: {str(e)}"}
        with open("pipeline_status.json", "w") as f:
            json.dump(state, f)
            
        print("📡 Telemetry sent! Open your Streamlit app and check Tab 3.")

if __name__ == "__main__":
    run_my_real_ml_pipeline()