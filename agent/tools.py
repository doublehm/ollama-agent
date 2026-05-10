import os
import subprocess

import httpx
from duckduckgo_search import DDGS
from langchain_core.tools import tool

from agent.confirm import ask_user_confirm


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
    result = subprocess.run(
        ["grep", "-rn", pattern, path],
        capture_output=True, text=True,
    )
    return result.stdout[:5000] if result.stdout else ""


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


all_tools = [
    read_file,
    list_dir,
    grep,
    get_processes,
    web_fetch,
    web_search,
    # confirm-required tools added in Task 4
]
