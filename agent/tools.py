import os
import signal
import subprocess
import shlex
import httpx
from ddgs import DDGS
from langchain_core.tools import StructuredTool, tool
from pydantic import BaseModel
import agent.confirm as confirm

# ── Auto-run tools ────────────────────────────────────────────────────────────

@tool
def read_file(path: str) -> str:
    """Read the contents of a file at the given path."""
    try:
        with open(path) as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"

@tool
def list_dir(path: str) -> str:
    """List the entries in a directory."""
    try:
        entries = sorted(os.listdir(path))
        return "\n".join(entries) if entries else "(empty directory)"
    except Exception as e:
        return f"Error listing {path}: {e}"

@tool
def grep(pattern: str, path: str) -> str:
    """Search for a regex pattern in a file or directory (recursive)."""
    try:
        result = subprocess.run(
            ["grep", "-rn", pattern, path],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout[:5000] if result.stdout else ""
    except subprocess.TimeoutExpired:
        return "Error: grep timed out after 10 seconds."

@tool
def get_processes() -> str:
    """List running processes."""
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    return result.stdout[:3000]

@tool
def web_fetch(url: str) -> str:
    """Fetch the text content of a URL (first 5000 characters)."""
    try:
        response = httpx.get(url, follow_redirects=True, timeout=10)
        return response.text[:5000]
    except Exception as e:
        return f"Error fetching {url}: {e}"

@tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return the top 5 results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found."
        lines = []
        for r in results:
            lines.append(f"- {r['title']}\n  {r['href']}\n  {r['body'][:200]}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Error searching: {e}"

# ── Confirm-required tools ────────────────────────────────────────────────────

@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file (creates or overwrites). Requires confirmation."""
    if not confirm.ask_user_confirm("write_file", {"path": path, "content": content[:120]}):
        return "Tool call declined by user."
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"

@tool
def run_shell(command: str) -> str:
    """Execute a command in fish shell. Requires confirmation."""
    if not confirm.ask_user_confirm("run_shell", {"command": command}):
        return "Tool call declined by user."
    try:
        result = subprocess.run(
            ["fish", "-c", command],
            capture_output=True, text=True, timeout=60,
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]: " + result.stderr
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 60 seconds."
    except Exception as e:
        return f"Error running command: {e}"

class _GitCmdInput(BaseModel):
    args: str

def _git_cmd_impl(args: str) -> str:
    if not confirm.ask_user_confirm("git_cmd", {"args": args}):
        return "Tool call declined by user."
    try:
        result = subprocess.run(
            ["git"] + shlex.split(args),
            capture_output=True, text=True, timeout=30
        )
        return (result.stdout + result.stderr).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: git command timed out after 30 seconds."
    except Exception as e:
        return f"Error running git {args}: {e}"

git_cmd = StructuredTool.from_function(
    func=_git_cmd_impl,
    name="git_cmd",
    description="Run a git subcommand (e.g. 'status', 'log --oneline -5'). Requires confirmation.",
    args_schema=_GitCmdInput,
)

@tool
def kill_process(pid: int) -> str:
    """Send SIGTERM to a process by PID. Requires confirmation."""
    if not confirm.ask_user_confirm("kill_process", {"pid": pid}):
        return "Tool call declined by user."
    try:
        os.kill(pid, signal.SIGTERM)
        return f"Sent SIGTERM to PID {pid}"
    except Exception as e:
        return f"Error killing PID {pid}: {e}"

from agent.vector_search import vector_search
from agent.toolkits.linux import journal_explorer, system_service_control, hardware_stats
from agent.toolkits.ds import run_ds_experiment
from agent.toolkits.design import get_ui_patterns
from agent.toolkits.cloud import terraform_validator, kubectl_navigator
from agent.toolkits.vision import capture_host_screen, capture_android_screen

all_tools = [
    read_file,
    list_dir,
    grep,
    get_processes,
    web_fetch,
    web_search,
    write_file,
    run_shell,
    git_cmd,
    kill_process,
    vector_search,
    journal_explorer,
    system_service_control,
    hardware_stats,
    run_ds_experiment,
    get_ui_patterns,
    terraform_validator,
    kubectl_navigator,
    capture_host_screen,
    capture_android_screen,
]

readonly_tools = [
    read_file,
    list_dir,
    grep,
    get_processes,
    web_fetch,
    web_search,
    vector_search,
    journal_explorer,
    hardware_stats,
    get_ui_patterns,
    capture_host_screen,
    capture_android_screen,
]
