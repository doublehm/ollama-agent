from langchain_ollama import ChatOllama

class ModelManager:
    # Model configuration: (model_name, num_gpu)
    MODELS = {
        "manager": ("llama3.3:70b", 0),
        "coder": ("qwen2.5-coder:32b", 10),
        "scientist": ("llama3.1:70b", 0),
        "designer": ("llama3.1:70b", 0),
        "cloud": ("llama3.1:70b", 0),
        "linux": ("llama3.3:70b", 0),
        "summarizer": ("qwen2.5:0.5b", 30),
        "vision": ("llava:7b", 30),
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
