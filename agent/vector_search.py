import os
import logging
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load a lightweight embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

IGNORE_DIRS = {
    '.git', '__pycache__', '.pytest_cache', 'node_modules', 
    'venv', '.venv', 'ollama_agent.egg-info', '.superpowers'
}

class VectorSearch:
    def __init__(self, directory: str):
        self.directory = directory
        self.files = []
        self._index = None
        self._initialized = False

    def refresh(self):
        self.files = []
        texts = []
        for root, dirs, files in os.walk(self.directory):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file.endswith(('.py', '.md', '.txt', '.java', '.kt', '.ts', '.tsx')):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():
                                self.files.append(path)
                                texts.append(content)
                    except:
                        continue
        
        if texts:
            embeddings = embedder.encode(texts)
            self._index = faiss.IndexFlatL2(embeddings.shape[1])
            self._index.add(np.array(embeddings).astype('float32'))
        
        self._initialized = True

    def search(self, query: str, k: int = 3) -> str:
        if not self._initialized:
            self.refresh()
            
        if self._index is None:
            return "No text files found to index."
        
        query_embedding = embedder.encode([query])
        distances, indices = self._index.search(np.array(query_embedding).astype('float32'), k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.files):
                results.append(self.files[idx])
        
        if not results:
            return "No relevant files found."
            
        return "Relevant files found: " + ", ".join(results)

# Instantiate searcher for the current directory
searcher = VectorSearch(os.getcwd())

@tool
def vector_search(query: str) -> str:
    """Semantic search across the codebase. Use this to find relevant files or context for complex questions."""
    return searcher.search(query)
