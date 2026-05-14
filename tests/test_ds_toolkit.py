import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from agent.toolkits.ds import run_ds_experiment

def test_run_ds_experiment_creates_folder_and_file():
    script = "print('hello')"
    # Mock subprocess to avoid actual execution
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="hello", stderr="")
        res = run_ds_experiment.func(script_content=script)
        
        assert "stdout" in res
        assert res["stdout"] == "hello"
        assert "run_directory" in res
        assert os.path.exists(res["run_directory"])
        
        # Cleanup
        if os.path.exists("experiments"):
            shutil.rmtree("experiments")

def test_run_ds_experiment_timeout():
    script = "import time; time.sleep(10)"
    with patch("subprocess.run", side_effect=Exception("Timeout simulated")):
        res = run_ds_experiment.func(script_content=script)
        assert "Error running experiment" in res
