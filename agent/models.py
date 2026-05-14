from langchain_ollama import ChatOllama

class ModelManager:
    # Model configuration: (model_name, num_gpu)
    MODELS = {
        "manager": ("llama3.3:70b", 0),      # IQ-heavy, CPU/RAM only
        "scientist": ("llama3.1:70b", 0),    # DS-heavy, CPU/RAM only
        "designer": ("llama3.1:70b", 0),     # Visual/spatial, CPU/RAM only
        "cloud": ("llama3.1:70b", 0),        # DevOps-heavy, CPU/RAM only
        "coder": ("qwen2.5-coder:32b", 10),  # Code-heavy, partial GPU
        "summarizer": ("qwen2.5:0.5b", 30),  # Background, full GPU
    }

    def get_model(self, role: str):
        config = self.MODELS.get(role, ("qwen2.5:latest", 10))
        model_name, num_gpu = config
        
        return ChatOllama(
            model=model_name,
            temperature=0,
            num_ctx=16384,
            num_gpu=num_gpu,
            keep_alive=0 # Aggressive eviction to avoid VRAM overlap on 6GB card
        )
