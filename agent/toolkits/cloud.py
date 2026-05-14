# agent/toolkits/cloud.py
import subprocess
from langchain_core.tools import tool

@tool
def terraform_validator(plan_path: str):
    """Validate a Terraform plan or file. Requires 'terraform' to be installed."""
    try:
        result = subprocess.run(["terraform", "validate", plan_path], capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running terraform: {e}"

@tool
def kubectl_navigator(command: str):
    """Execute a kubectl command (e.g., 'get pods', 'logs <pod>'). Safe read-only commands recommended."""
    # For safety, we only allow certain commands here, or rely on the host confirmation loop
    try:
        result = subprocess.run(["kubectl"] + command.split(), capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running kubectl: {e}"
