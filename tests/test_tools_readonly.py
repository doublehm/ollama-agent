import pytest
from agent.tools import read_file, list_dir, grep, get_processes


def test_read_file_returns_content(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hello world")
    result = read_file.invoke({"path": str(f)})
    assert result == "hello world"


def test_read_file_missing_returns_error_message(tmp_path):
    result = read_file.invoke({"path": str(tmp_path / "nope.txt")})
    assert "error" in result.lower() or "Error" in result


def test_list_dir_returns_filenames(tmp_path):
    (tmp_path / "alpha.txt").write_text("x")
    (tmp_path / "beta.py").write_text("y")
    result = list_dir.invoke({"path": str(tmp_path)})
    assert "alpha.txt" in result
    assert "beta.py" in result


def test_list_dir_missing_path_returns_error():
    result = list_dir.invoke({"path": "/nonexistent/path/xyz"})
    assert "error" in result.lower() or "Error" in result


def test_grep_finds_match(tmp_path):
    f = tmp_path / "code.py"
    f.write_text("def hello():\n    pass\n")
    result = grep.invoke({"pattern": "def hello", "path": str(f)})
    assert "def hello" in result


def test_grep_no_match_returns_empty_or_message(tmp_path):
    f = tmp_path / "code.py"
    f.write_text("x = 1\n")
    result = grep.invoke({"pattern": "ZZZNOMATCH", "path": str(f)})
    assert result == "" or "no match" in result.lower()


def test_get_processes_returns_process_list():
    result = get_processes.invoke({})
    assert len(result) > 10
    assert "PID" in result or "pid" in result.lower()
