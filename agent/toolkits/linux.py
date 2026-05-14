# agent/toolkits/linux.py
import subprocess
import os
from langchain_core.tools import tool
from agent.confirm import ask_user_confirm

@tool
def journal_explorer(query: str, lines: int = 50):
    """Search system logs using journalctl. Example: query='error'."""
    cmd = ["journalctl", "-n", str(lines), "--no-pager"]
    if query:
        cmd.extend(["-g", query])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.stdout or "No matching logs found."
    except subprocess.TimeoutExpired:
        return "Error: journalctl command timed out after 15 seconds."
    except Exception as e:
        return f"Error reading logs: {e}"

@tool
def system_service_control(service: str, action: str):
    """Control systemd services (status, start, stop, restart). Action: 'status' is safe."""
    if action != "status":
        if not ask_user_confirm("system_service_control", {"service": service, "action": action}):
            return "Action cancelled by user."

    try:
        result = subprocess.run(["systemctl", action, service], capture_output=True, text=True, timeout=10)
        return (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired:
        return "Error: systemctl command timed out after 10 seconds."
    except Exception as e:
        return f"Error controlling service: {e}"

@tool
def hardware_stats():
    """Get real-time GPU/CPU/RAM utilization."""
    stats = []
    try:
        # GPU stats (NVIDIA)
        gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5).stdout
        if gpu:
            stats.append(f"GPU: {gpu.strip()}")
    except:
        stats.append("GPU: N/A")

    try:
        # CPU stats (Linux)
        # Using top to get idle percentage and then subtracting from 100
        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/'"
        idle = subprocess.run(cpu_cmd, shell=True, capture_output=True, text=True, timeout=5).stdout.strip()
        if idle:
            util = 100 - float(idle)
            stats.append(f"CPU Util: {util:.1f}%")
    except:
        stats.append("CPU Util: N/A")

    try:
        # RAM stats
        mem = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=5).stdout
        if mem:
            stats.append(f"Memory:\n{mem.strip()}")
    except:
        stats.append("Memory: N/A")

    return "\n".join(stats)
