import os
from unittest.mock import patch
import pytest
from agent.tools import write_file, run_shell, git_cmd, kill_process


def test_write_file_confirmed_creates_file(tmp_path):
    target = str(tmp_path / "out.txt")
    with patch("agent.confirm.ask_user_confirm", return_value=True):
        result = write_file.invoke({"path": target, "content": "hello"})
    assert "Written" in result
    assert open(target).read() == "hello"


def test_write_file_declined_does_not_create_file(tmp_path):
    target = str(tmp_path / "out.txt")
    with patch("agent.confirm.ask_user_confirm", return_value=False):
        result = write_file.invoke({"path": target, "content": "hello"})
    assert "declined" in result.lower()
    assert not os.path.exists(target)


def test_run_shell_confirmed_executes_command():
    with patch("agent.confirm.ask_user_confirm", return_value=True):
        result = run_shell.invoke({"command": "echo ollama-agent-test"})
    assert "ollama-agent-test" in result


def test_run_shell_declined_does_not_execute():
    with patch("agent.confirm.ask_user_confirm", return_value=False):
        result = run_shell.invoke({"command": "echo should-not-run"})
    assert "declined" in result.lower()


def test_git_cmd_declined_does_not_run():
    with patch("agent.confirm.ask_user_confirm", return_value=False):
        result = git_cmd.invoke({"args": "status"})
    assert "declined" in result.lower()


def test_kill_process_declined_does_not_kill():
    with patch("agent.confirm.ask_user_confirm", return_value=False):
        result = kill_process.invoke({"pid": 99999})
    assert "declined" in result.lower()
