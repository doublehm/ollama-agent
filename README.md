# ollama-agent

Local Claude Code-style agentic CLI powered by Ollama (gemma4:latest) and LangGraph.

## Requirements

- Ollama running locally with `gemma4:latest` pulled
- Python 3.12+
- fish shell

## Install

```bash
pip3 install langgraph langchain-ollama langchain-core "ddgs>=8.1"
```

## Run

```bash
cd ~/ollama-agent
python3 repl.py
```

## Commands

| Command | Action |
|---------|--------|
| `/clear` | Reset conversation history |
| `/exit` | Quit |
| `Ctrl+C` | Quit |

## Tools

| Tool | Confirmation | Description |
|------|-------------|-------------|
| `read_file` | No | Read file contents |
| `list_dir` | No | List directory entries |
| `grep` | No | Search for patterns |
| `get_processes` | No | List running processes |
| `web_fetch` | No | Fetch a URL |
| `web_search` | No | DuckDuckGo search |
| `write_file` | Yes | Write/overwrite a file |
| `run_shell` | Yes | Execute a fish shell command |
| `git_cmd` | Yes | Run a git subcommand |
| `kill_process` | Yes | Send SIGTERM to a process |
