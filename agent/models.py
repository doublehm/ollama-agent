from langchain_ollama import ChatOllama

class ModelManager:
    # Model configuration: (model_name, num_gpu)
    # Optimized for May 2026 state-of-the-art: Gemma 4
    # Gemma 4 31B is natively agentic and multimodal, fitting perfectly in 32GB RAM.
    MODELS = {
        "manager": ("gemma4:31b", 10),       # Lead Architect
        "coder": ("gemma4:31b", 10),         # Developer
        "scientist": ("gemma4:31b", 10),     # Scientist
        "designer": ("gemma4:31b", 10),      # Designer (Native Vision)
        "cloud": ("gemma4:31b", 10),         # Cloud Expert
        "linux": ("gemma4:31b", 10),         # Linux Expert
        "summarizer": ("gemma4:latest", 30), # Background (9B class)
        "vision": ("gemma4:31b", 10),        # Unified Vision support
    }

    def get_model(self, role: str):
        config = self.MODELS.get(role, ("gemma4:latest", 10))
        model_name, num_gpu = config
        
        return ChatOllama(
            model=model_name,
            temperature=0,
            num_ctx=16384,
            num_gpu=num_gpu,
            keep_alive=0 # Aggressive eviction
        )
