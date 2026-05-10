from unittest.mock import patch
from agent.confirm import needs_confirmation, ask_user_confirm


def test_write_file_needs_confirmation():
    assert needs_confirmation("write_file") is True


def test_run_shell_needs_confirmation():
    assert needs_confirmation("run_shell") is True


def test_git_cmd_needs_confirmation():
    assert needs_confirmation("git_cmd") is True


def test_kill_process_needs_confirmation():
    assert needs_confirmation("kill_process") is True


def test_read_file_no_confirmation():
    assert needs_confirmation("read_file") is False


def test_list_dir_no_confirmation():
    assert needs_confirmation("list_dir") is False


def test_grep_no_confirmation():
    assert needs_confirmation("grep") is False


def test_web_fetch_no_confirmation():
    assert needs_confirmation("web_fetch") is False


def test_ask_user_confirm_yes_returns_true():
    with patch("builtins.input", return_value="y"):
        assert ask_user_confirm("run_shell", {"command": "ls"}) is True


def test_ask_user_confirm_no_returns_false():
    with patch("builtins.input", return_value="n"):
        assert ask_user_confirm("run_shell", {"command": "ls"}) is False


def test_ask_user_confirm_empty_defaults_to_false():
    with patch("builtins.input", return_value=""):
        assert ask_user_confirm("run_shell", {"command": "ls"}) is False


def test_ask_user_confirm_eof_returns_false():
    with patch("builtins.input", side_effect=EOFError):
        assert ask_user_confirm("write_file", {"path": "/tmp/x", "content": "y"}) is False
