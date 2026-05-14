from agent.models import ModelManager

def test_model_resolution():
    manager = ModelManager()
    
    # Manager: 70B, CPU only
    manager_model = manager.get_model("manager")
    assert manager_model.model == "llama3.3:70b"
    assert manager_model.num_gpu == 0
    
    # Coder: 32B, Partial GPU
    coder_model = manager.get_model("coder")
    assert coder_model.model == "qwen2.5-coder:32b"
    assert coder_model.num_gpu == 10
    
    # Summarizer: 0.5B, Full GPU
    summarizer_model = manager.get_model("summarizer")
    assert summarizer_model.model == "qwen2.5:0.5b"
    assert summarizer_model.num_gpu == 30
    
    # Fallback
    fallback_model = manager.get_model("unknown")
    assert fallback_model.model == "qwen2.5:latest"
    assert fallback_model.num_gpu == 10

def test_get_vision_model():
    manager = ModelManager()
    model = manager.get_model("vision")
    assert model.model == "llava:7b"
    assert model.num_gpu == 30
    assert model.keep_alive == 0

def test_aggressive_eviction():
    manager = ModelManager()
    model = manager.get_model("manager")
    assert model.keep_alive == 0
