from langchain_ollama import ChatOllama

class ModelManager:
    # Model configuration: (model_name, num_gpu)
    # Downgraded from 70B to 32B to fit in 32GB RAM / 6GB VRAM
    MODELS = {
        "manager": ("qwen2.5:32b", 10),      # High-IQ reasoning, fits in RAM+VRAM
        "coder": ("qwen2.5-coder:32b", 10),  # Top-tier coding
        "scientist": ("qwen2.5:32b", 10),    # DS/ML Logic
        "designer": ("qwen2.5:32b", 10),     # UI/UX Reasoning
        "cloud": ("qwen2.5:32b", 10),       # DevOps Logic
        "linux": ("qwen2.5:32b", 10),       # System Admin
        "summarizer": ("qwen2.5:0.5b", 30),  # Background, full GPU
        "vision": ("llava:7b", 30),          # Vision
    }

    def get_model(self, role: str):
        config = self.MODELS.get(role, ("qwen2.5:32b", 10))
        model_name, num_gpu = config
        
        return ChatOllama(
            model=model_name,
            temperature=0,
            num_ctx=16384,
            num_gpu=num_gpu,
            keep_alive=0 # Aggressive eviction to avoid VRAM overlap
        )
