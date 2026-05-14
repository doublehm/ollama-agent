# agent/toolkits/vision.py
import subprocess
import os
import datetime
from langchain_core.tools import tool

def _get_experiment_path(prefix: str, ext: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{ext}"
    return os.path.abspath(os.path.join("experiments", filename))

@tool
def capture_host_screen() -> str:
    """Capture the host desktop screen using gnome-screenshot. Returns the path to the saved image."""
    output_path = _get_experiment_path("host_screenshot", "png")
    
    # Check if gnome-screenshot is installed
    if subprocess.run(["which", "gnome-screenshot"], capture_output=True).returncode != 0:
        return "Error: gnome-screenshot is not installed on the host system."
    
    try:
        # gnome-screenshot -f <path>
        result = subprocess.run(
            ["gnome-screenshot", "-f", output_path],
            capture_output=True,
            text=True,
            timeout=20
        )
        if result.returncode == 0:
            return output_path
        else:
            return f"Error capturing host screen: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: gnome-screenshot timed out after 20 seconds."
    except Exception as e:
        return f"Error capturing host screen: {e}"

@tool
def capture_android_screen() -> str:
    """Capture the connected Android device screen using adb. Returns the path to the saved image."""
    output_path = _get_experiment_path("android_screenshot", "png")
    
    # Check if adb is installed
    if subprocess.run(["which", "adb"], capture_output=True).returncode != 0:
        return "Error: adb is not installed on the host system."
    
    try:
        # Check if any device is connected
        devices = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10).stdout
        if "device" not in devices.splitlines()[1:]:
             return "Error: No Android device connected or authorized via adb."

        # adb exec-out screencap -p > output_path
        with open(output_path, "wb") as f:
            result = subprocess.run(
                ["adb", "exec-out", "screencap", "-p"],
                stdout=f,
                stderr=subprocess.PIPE,
                timeout=30
            )
        
        if result.returncode == 0:
            return output_path
        else:
            # Cleanup failed file
            if os.path.exists(output_path):
                os.remove(output_path)
            return f"Error capturing Android screen: {result.stderr.decode()}"
    except subprocess.TimeoutExpired:
        if os.path.exists(output_path):
            os.remove(output_path)
        return "Error: adb screencap timed out after 30 seconds."
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        return f"Error capturing Android screen: {e}"
