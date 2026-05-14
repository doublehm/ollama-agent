#!/usr/bin/env python3
import sys
import os
import json
import re

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
    messages_to_dict,
    messages_from_dict
)
from agent.graph import build_graph
import agent.confirm
from agent.toolkits.mcp_hub import MCPHub
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

console = Console()

import re

def strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def log_markdown(content: str):
    try:
        clean_content = strip_ansi(content)
        with open(".ollama-agent.md", "a", encoding="utf-8") as f:
            f.write(clean_content + "\n")
    except Exception as e:
        print(f"[warning] failed to write log: {e}")

def save_state(history, state_file):
    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(messages_to_dict(history), f, indent=2)
    except Exception as e:
        console.print(f"[bold red]failed to save state: {e}[/bold red]")

def sanitize_history(history):
    # Do a full sweep of the history to find any orphaned tool calls or tool messages.
    # If a corruption is found, truncate the history from that point forward to ensure it is valid.
    valid_history = []
    i = 0
    while i < len(history):
        msg = history[i]
        valid_history.append(msg)
        
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            expected = len(msg.tool_calls)
            is_valid = True
            j = i + 1
            while j < len(history) and expected > 0:
                if isinstance(history[j], ToolMessage):
                    valid_history.append(history[j])
                    expected -= 1
                    j += 1
                else:
                    is_valid = False
                    break
            if not is_valid or expected > 0:
                valid_history.pop()
                break
            i = j - 1
        elif isinstance(msg, ToolMessage):
            valid_history.pop()
            break
        i += 1
    return valid_history

def trim_history(history, max_messages=40):
    if len(history) <= max_messages:
        return history
    
    # We want to keep at most max_messages.
    # Find the earliest HumanMessage within the last max_messages.
    target_start = len(history) - max_messages
    for i in range(target_start, len(history)):
        if isinstance(history[i], HumanMessage):
            return history[i:]
            
    # If no HumanMessage found in the window, just return the last max_messages
    return history[-max_messages:]

async def main():
    print("Universal Expert Assistant (Local) — /clear to reset, /resume to load chat, /yolo to toggle auto-run, /mcp for tools, /exit to quit\n")
    
    mcp_hub = MCPHub()
    mcp_tools = await mcp_hub.initialize()
    
    graph = build_graph(mcp_tools=mcp_tools)
    history = []
    state_file = ".ollama-agent-state.json"

    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                history = sanitize_history(messages_from_dict(data))
            console.print("[dim]Resumed previous session. Use /clear to start over.[/dim]\n")
        except Exception as e:
            console.print(f"[bold red]Failed to load previous session: {e}[/bold red]\n")

    log_markdown("# Ollama Agent Session Started\n")

    command_completer = WordCompleter(['/clear', '/exit', '/yolo', '/resume', '/mcp'], ignore_case=True)
    session = PromptSession(completer=command_completer)

    while True:
        try:
            user_input = session.prompt("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            await mcp_hub.shutdown()
            sys.exit(0)

        if not user_input:
            continue
        if user_input == "/exit":
            print("Bye.")
            await mcp_hub.shutdown()
            sys.exit(0)
        if user_input == "/mcp":
            console.print("\n[bold]Active MCP Tools:[/bold]")
            if not mcp_tools:
                console.print("  [dim]No MCP tools active.[/dim]")
            else:
                for t in mcp_tools:
                    desc = t.description[:80] + "..." if len(t.description) > 80 else t.description
                    console.print(f"  [green]{t.name}[/green]: {desc}")
            print()
            continue
        if user_input == "/clear":
            history = []
            if os.path.exists(state_file):
                try:
                    import time
                    backup_file = f".ollama-agent-state-{int(time.time())}.json"
                    os.rename(state_file, backup_file)
                    console.print(f"[dim]Previous chat saved as {backup_file}[/dim]")
                except Exception:
                    pass
            print("[conversation cleared]\n")
            log_markdown("---\n**[Conversation Cleared]**\n")
            continue
        if user_input == "/yolo":
            agent.confirm.YOLO_MODE = not agent.confirm.YOLO_MODE
            state_str = "ON" if agent.confirm.YOLO_MODE else "OFF"
            console.print(f"[bold red]YOLO Mode is now {state_str}[/bold red]")
            log_markdown(f"---\n**[YOLO Mode: {state_str}]**\n")
            continue
        if user_input == "/resume":
            import glob
            backups = sorted(glob.glob(".ollama-agent-state-*.json"))
            if not backups:
                console.print("[dim]No saved chats found.[/dim]")
                continue
            
            console.print("\n[bold]Available saved chats:[/bold]")
            for i, f in enumerate(backups):
                mtime = os.path.getmtime(f)
                import datetime
                time_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                console.print(f"  [{i+1}] {f} ({time_str})")
            
            choice = session.prompt("\nEnter number to resume (or press Enter to cancel): ").strip()
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(backups):
                console.print("[dim]Cancelled resume.[/dim]")
                continue
            
            selected_file = backups[int(choice)-1]
            
            if history and os.path.exists(state_file):
                import time
                backup_file = f".ollama-agent-state-{int(time.time())}.json"
                os.rename(state_file, backup_file)
                console.print(f"[dim]Current chat saved as {backup_file}[/dim]")
            
            try:
                with open(selected_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    history = sanitize_history(messages_from_dict(data))
                save_state(history, state_file)
                console.print(f"[bold green]Successfully resumed chat from {time_str}[/bold green]")
                log_markdown(f"---\n**[Resumed chat from {selected_file}]**\n")
            except Exception as e:
                console.print(f"[bold red]Failed to load session: {e}[/bold red]")
            continue

        history_backup = list(history)
        history.append(HumanMessage(content=user_input))
        log_markdown(f"## User\n\n{user_input}\n")

        print()
        last_snapshot = None
        try:
            # Trim history to fit model context window and prevent hallucination
            trimmed_history = trim_history(history)
            processed_count = len(trimmed_history)
            for snapshot in graph.stream(
                {"messages": trimmed_history, "mcp_tools": mcp_tools},
                stream_mode="values",
            ):
                last_snapshot = snapshot
                new_msgs = snapshot["messages"][processed_count:]
                for msg in new_msgs:
                    if isinstance(msg, AIMessage):
                        if msg.content:
                            console.print(Markdown(msg.content))
                            log_markdown(f"## Assistant\n\n{msg.content}\n")
                        if getattr(msg, "tool_calls", None):
                            for tc in msg.tool_calls:
                                log_markdown(f"**Tool Call:** `{tc.get('name')}`\n```json\n{tc.get('args')}\n```\n")
                    elif isinstance(msg, ToolMessage):
                        log_markdown(f"**Tool Result ({msg.name}):**\n```\n{msg.content}\n```\n")
                
                processed_count = len(snapshot["messages"])
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Cancelled.[/bold yellow]")
            log_markdown("**[Cancelled by User]**\n")
            history = sanitize_history(history_backup)
            save_state(history, state_file)
            continue
        except Exception as e:
            console.print(f"[bold red][Error]: {e}[/bold red]")
            log_markdown(f"**[Error]:** {e}\n")
            history = sanitize_history(history_backup)
            save_state(history, state_file)
            continue

        if last_snapshot:
            # Append only the new messages to the full history
            new_msgs_final = last_snapshot["messages"][len(trimmed_history):]
            history.extend(new_msgs_final)
            save_state(history, state_file)

        print()


if __name__ == "__main__":
    asyncio.run(main())