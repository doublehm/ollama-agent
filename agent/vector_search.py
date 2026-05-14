import os
import logging
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load a lightweight embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

class VectorSearch:
    def __init__(self, directory: str):
        self.directory = directory
        self.files = []
        self.embeddings = []
        self._index = None
        self.refresh()

    def refresh(self):
        self.files = []
        texts = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(('.py', '.md', '.txt', '.java', '.kt')):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            self.files.append(path)
                            texts.append(content)
                    except:
                        continue
        
        if texts:
            self.embeddings = embedder.encode(texts)
            self._index = faiss.IndexFlatL2(self.embeddings.shape[1])
            self._index.add(np.array(self.embeddings).astype('float32'))

    def search(self, query: str, k: int = 3) -> str:
        if self._index is None:
            return "Index not built."
        
        query_embedding = embedder.encode([query])
        distances, indices = self._index.search(np.array(query_embedding).astype('float32'), k)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.files):
                results.append(self.files[idx])
        
        return "Relevant files found: " + ", ".join(results)

# Instantiate searcher for the current directory
searcher = VectorSearch(os.getcwd())

@tool
def vector_search(query: str) -> str:
    """Semantic search across the codebase. Use this to find relevant files or context for complex questions."""
    return searcher.search(query)
