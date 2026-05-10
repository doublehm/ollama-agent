_CONFIRM_TOOLS = {"write_file", "run_shell", "kill_process", "git_cmd"}


def needs_confirmation(tool_name: str) -> bool:
    return tool_name in _CONFIRM_TOOLS


def ask_user_confirm(tool_name: str, params: dict) -> bool:
    print(f"\n[tool: {tool_name}]")
    for key, val in params.items():
        print(f"  {key}: {val!r}")
    try:
        answer = input("Run? [y/N]: ").strip().lower()
    except EOFError:
        return False
    return answer == "y"
