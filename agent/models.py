from langchain_ollama import ChatOllama

class ModelManager:
    MODELS = {
        "manager": "llama3.3:70b", # IQ-heavy
        "coder": "qwen2.5-coder:32b", # Code-heavy
        "summarizer": "qwen2.5:0.5b" # Background
    }

    def get_model(self, role: str):
        model_name = self.MODELS.get(role, "qwen2.5:latest")
        # Optimization for 6GB VRAM
        # We use num_gpu=0 for the 70B (CPU/RAM) 
        # and partial offload for 32B
        num_gpu = 0 if "70b" in model_name else 30 
        
        return ChatOllama(
            model=model_name,
            temperature=0,
            num_ctx=16384,
            num_gpu=num_gpu,
            keep_alive="5m" # Unload after 5m of inactivity
        )
