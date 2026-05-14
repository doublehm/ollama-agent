# agent/toolkits/linux.py
import subprocess
from langchain_core.tools import tool

@tool
def journal_explorer(query: str, lines: int = 50):
    """Search system logs using journalctl. Example: query='error'."""
    cmd = ["journalctl", "-n", str(lines), "--no-pager"]
    if query:
        cmd.extend(["-g", query])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout or "No matching logs found."

@tool
def system_service_control(service: str, action: str):
    """Control systemd services (status, start, stop, restart). Action: 'status' is safe."""
    result = subprocess.run(["systemctl", action, service], capture_output=True, text=True)
    return result.stdout + result.stderr

@tool
def hardware_stats():
    """Get real-time GPU/CPU/RAM utilization."""
    try:
        gpu = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout
    except:
        gpu = "N/A"
    try:
        cpu = subprocess.run(["grep", "cpu ", "/proc/stat"], capture_output=True, text=True).stdout
    except:
        cpu = "N/A"
    return f"GPU Util: {gpu.strip()}%, CPU Raw: {cpu.strip()}"
