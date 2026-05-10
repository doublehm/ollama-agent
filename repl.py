#!/usr/bin/env python3
import sys

from langchain_core.messages import AIMessage, AIMessageChunk
from agent.graph import build_graph


def main():
    print("Ollama Agent (gemma4:latest) — /clear to reset, /exit to quit\n")
    graph = build_graph()
    history = []

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            sys.exit(0)

        if not user_input:
            continue
        if user_input == "/exit":
            print("Bye.")
            sys.exit(0)
        if user_input == "/clear":
            history = []
            print("[conversation cleared]\n")
            continue

        from langchain_core.messages import HumanMessage
        history.append(HumanMessage(content=user_input))

        print()
        last_snapshot = None
        try:
            for snapshot in graph.stream(
                {"messages": history},
                stream_mode="values",
            ):
                last_snapshot = snapshot
                new_msgs = snapshot["messages"][len(history):]
                for msg in new_msgs:
                    if (
                        isinstance(msg, AIMessage)
                        and msg.content
                        and not getattr(msg, "tool_calls", None)
                    ):
                        print(msg.content, flush=True)
        except Exception as e:
            print(f"[error]: {e}")
            history.pop()
            continue

        if last_snapshot:
            history = last_snapshot["messages"]

        print()


if __name__ == "__main__":
    main()
