import pytest
from unittest.mock import patch, MagicMock
import subprocess
from agent.toolkits.linux import journal_explorer, system_service_control, hardware_stats

def test_journal_explorer_calls_with_timeout():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="logs")
        journal_explorer.func(query="error")
        args, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 15

@patch("agent.toolkits.linux.ask_user_confirm")
@patch("subprocess.run")
def test_system_service_control_status_no_confirm(mock_run, mock_confirm):
    mock_run.return_value = MagicMock(stdout="active", stderr="")
    system_service_control.func(service="nginx", action="status")
    mock_confirm.assert_not_called()

@patch("agent.toolkits.linux.ask_user_confirm")
@patch("subprocess.run")
def test_system_service_control_restart_needs_confirm(mock_run, mock_confirm):
    mock_confirm.return_value = True
    mock_run.return_value = MagicMock(stdout="", stderr="")
    system_service_control.func(service="nginx", action="restart")
    mock_confirm.assert_called_once()

@patch("subprocess.run")
def test_hardware_stats(mock_run):
    # Mock multiple calls
    m1 = MagicMock(stdout="GPU INFO")
    m2 = MagicMock(stdout="5.5") # idle 94.5%
    m3 = MagicMock(stdout="MEM INFO")
    mock_run.side_effect = [m1, m2, m3]
    
    res = hardware_stats.func()
    assert "GPU INFO" in res
    assert "CPU Util: 94.5%" in res
    assert "MEM INFO" in res
