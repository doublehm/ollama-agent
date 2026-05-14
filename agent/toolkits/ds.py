# agent/toolkits/ds.py
import subprocess
import os
import uuid
from langchain_core.tools import tool

@tool
def run_ds_experiment(script_content: str):
    """Write and run a Python DS script in an isolated folder. Captures stdout and any generated plots."""
    # Create unique run directory
    run_id = str(uuid.uuid4())[:8]
    exp_dir = f"experiments/run_{run_id}"
    os.makedirs(exp_dir, exist_ok=True)
    
    script_path = os.path.join(exp_dir, "experiment.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    try:
        # Run from the experiment directory so files are created there
        result = subprocess.run(
            ["python3", "experiment.py"], 
            cwd=exp_dir,
            capture_output=True, 
            text=True, 
            timeout=300 # Longer timeout for ML training
        )
        
        # Collect all files created in the exp_dir (excluding the script)
        files = os.listdir(exp_dir)
        generated_files = [f for f in files if f != "experiment.py"]
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "generated_files": [os.path.join(exp_dir, f) for f in generated_files],
            "run_directory": exp_dir
        }
    except subprocess.TimeoutExpired:
        return f"Error: Experiment timed out after 300 seconds in {exp_dir}."
    except Exception as e:
        return f"Error running experiment: {e}"
