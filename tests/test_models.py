from agent.models import ModelManager

def test_model_resolution():
    manager = ModelManager()
    
    # Manager: Gemma 4 31B
    manager_model = manager.get_model("manager")
    assert manager_model.model == "gemma4:31b"
    assert manager_model.num_gpu == 10
    
    # Coder: Gemma 4 31B
    coder_model = manager.get_model("coder")
    assert coder_model.model == "gemma4:31b"
    assert coder_model.num_gpu == 10
    
    # Summarizer: Gemma 4 9B (latest)
    summarizer_model = manager.get_model("summarizer")
    assert summarizer_model.model == "gemma4:latest"
    assert summarizer_model.num_gpu == 30
    
    # Fallback
    fallback_model = manager.get_model("unknown")
    assert fallback_model.model == "gemma4:latest"
    assert fallback_model.num_gpu == 10

def test_aggressive_eviction():
    manager = ModelManager()
    model = manager.get_model("manager")
    assert model.keep_alive == 0
