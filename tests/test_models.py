from agent.models import ModelManager

def test_model_resolution():
    manager = ModelManager()
    
    manager_model = manager.get_model("manager")
    assert manager_model.model == "llama3.3:70b"
    assert manager_model.num_gpu == 0
    
    coder_model = manager.get_model("coder")
    assert coder_model.model == "qwen2.5-coder:32b"
    assert coder_model.num_gpu == 30
