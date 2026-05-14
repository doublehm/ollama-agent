import os
import logging
import importlib
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from tree_sitter import Parser, Language

# Load a lightweight embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

IGNORE_DIRS = {
    '.git', '__pycache__', '.pytest_cache', 'node_modules', 
    'venv', '.venv', 'ollama_agent.egg-info', '.superpowers',
    'experiments'
}

EXTENSION_TO_LANG = {
    '.py': ('tree_sitter_python', 'python'),
    '.js': ('tree_sitter_javascript', 'javascript'),
    '.ts': ('tree_sitter_typescript', 'typescript'),
    '.tsx': ('tree_sitter_typescript', 'tsx'),
    '.java': ('tree_sitter_java', 'java'),
    # Kotlin often uses the same parser as Java or a specific one if available
}

# Relevant node types for different languages
NODE_TYPES = {
    'python': {'function_definition', 'class_definition'},
    'javascript': {'function_declaration', 'class_declaration', 'method_definition'},
    'typescript': {'function_declaration', 'class_declaration', 'method_definition', 'interface_declaration', 'type_alias_declaration'},
    'tsx': {'function_declaration', 'class_declaration', 'method_definition', 'interface_declaration', 'type_alias_declaration'},
    'java': {'class_declaration', 'method_declaration', 'interface_declaration', 'enum_declaration'},
}

class VectorSearch:
    def __init__(self, directory: str):
        self.directory = directory
        self.chunks = []  # List of dicts with 'text', 'path', 'line'
        self._index = None
        self._initialized = False
        self._lang_cache = {}

    def _get_language(self, pkg_name: str):
        if pkg_name in self._lang_cache:
            return self._lang_cache[pkg_name]
        try:
            mod = importlib.import_module(pkg_name)
            lang = Language(mod.language())
            self._lang_cache[pkg_name] = lang
            return lang
        except Exception as e:
            logging.warning(f"Could not load language package {pkg_name}: {e}")
            return None

    def _get_chunks(self, content: str, path: str) -> list[dict]:
        ext = os.path.splitext(path)[1]
        lang_info = EXTENSION_TO_LANG.get(ext)
        
        if not lang_info:
            return self._fallback_chunking(content, path)
            
        pkg_name, lang_name = lang_info
        language = self._get_language(pkg_name)
        
        if not language:
            return self._fallback_chunking(content, path)
            
        try:
            parser = Parser(language)
            tree = parser.parse(bytes(content, 'utf8'))
            
            chunks = []
            target_types = NODE_TYPES.get(lang_name, set())
            
            def walk(node):
                if node.type in target_types:
                    start_line = node.start_point[0] + 1
                    text = content[node.start_byte:node.end_byte]
                    chunks.append({
                        'text': f"File: {path}\nLanguage: {lang_name}\nCode:\n{text}",
                        'path': path,
                        'line': start_line
                    })
                # Continue walking children regardless if we found a match (e.g. methods in a class)
                for child in node.children:
                    walk(child)
            
            walk(tree.root_node)
            
            if not chunks:
                return self._fallback_chunking(content, path)
            return chunks
            
        except Exception as e:
            logging.error(f"Error parsing {path}: {e}")
            return self._fallback_chunking(content, path)

    def _fallback_chunking(self, content: str, path: str) -> list[dict]:
        lines = content.splitlines()
        chunks = []
        chunk_size = 50
        # If file is very short, just one chunk
        if len(lines) <= chunk_size:
            chunks.append({
                'text': f"File: {path}\nCode:\n{content}",
                'path': path,
                'line': 1
            })
            return chunks
            
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            text = "\n".join(chunk_lines)
            chunks.append({
                'text': f"File: {path}\nCode:\n{text}",
                'path': path,
                'line': i + 1
            })
        return chunks

    def refresh(self):
        self.chunks = []
        texts = []
        for root, dirs, files in os.walk(self.directory):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file.endswith(('.py', '.md', '.txt', '.java', '.kt', '.ts', '.tsx', '.js')):
                    path = os.path.join(root, file)
                    try:
                        # Skip files larger than 1MB
                        if os.path.getsize(path) > 1024 * 1024:
                            continue
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():
                                file_chunks = self._get_chunks(content, path)
                                for chunk in file_chunks:
                                    self.chunks.append(chunk)
                                    texts.append(chunk['text'])
                    except:
                        continue
        
        if texts:
            embeddings = embedder.encode(texts)
            self._index = faiss.IndexFlatL2(embeddings.shape[1])
            self._index.add(np.array(embeddings).astype('float32'))
        
        self._initialized = True

    def search(self, query: str, k: int = 5) -> str:
        if not self._initialized:
            self.refresh()
            
        if self._index is None:
            return "No text files found to index."
        
        query_embedding = embedder.encode([query])
        distances, indices = self._index.search(np.array(query_embedding).astype('float32'), k)
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.chunks):
                chunk = self.chunks[idx]
                results.append(f"{chunk['path']}:{chunk['line']}")
        
        if not results:
            return "No relevant files found."
            
        # De-duplicate results while preserving order
        unique_results = []
        seen = set()
        for r in results:
            if r not in seen:
                unique_results.append(r)
                seen.add(r)
        
        return "Relevant locations found: " + ", ".join(unique_results)

# Instantiate searcher for the current directory
searcher = VectorSearch(os.getcwd())

@tool
def vector_search(query: str) -> str:
    """Semantic search across the codebase. Use this to find relevant code blocks or context for complex questions."""
    return searcher.search(query)
