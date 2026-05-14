# agent/toolkits/ds.py
import subprocess
import os
from langchain_core.tools import tool

@tool
def run_ds_experiment(script_content: str):
    """Write and run a Python DS script. Saves plots to 'experiments/' folder."""
    os.makedirs("experiments", exist_ok=True)
    # Generate unique filename to avoid collisions
    import time
    timestamp = int(time.time())
    path = f"experiments/exp_{timestamp}.py"
    with open(path, "w") as f:
        f.write(script_content)
    
    try:
        result = subprocess.run(["python3", path], capture_output=True, text=True, timeout=180)
        files = os.listdir("experiments")
        # Find files created during this experiment (simple check)
        plots = [f for f in files if f.endswith(('.png', '.jpg', '.html'))]
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "generated_plots": plots,
            "script_path": path
        }
    except subprocess.TimeoutExpired:
        return "Error: Experiment timed out after 180 seconds."
