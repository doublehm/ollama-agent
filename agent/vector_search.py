import os
import logging
import importlib
import pickle
import json
import time
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
from langchain_core.tools import tool
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from tree_sitter import Parser, Language

# Load a lightweight embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

INDEX_DIR = os.path.join(os.getcwd(), '.ollama-agent', 'index')
MANIFEST_PATH = os.path.join(INDEX_DIR, 'manifest.json')
METADATA_PATH = os.path.join(INDEX_DIR, 'metadata.pkl')
FAISS_INDEX_PATH = os.path.join(INDEX_DIR, 'index.faiss')

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
        self.chunks = []  # List of dicts with 'text', 'path', 'line', 'embedding'
        self.manifest = {}  # dict mapping path to mtime
        self._index = None
        self._initialized = False
        self._lang_cache = {}
        self.load()

    def load(self):
        if not os.path.exists(INDEX_DIR):
            return
            
        try:
            if os.path.exists(MANIFEST_PATH):
                with open(MANIFEST_PATH, 'r') as f:
                    self.manifest = json.load(f)
            
            if os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, 'rb') as f:
                    self.chunks = pickle.load(f)
            
            if os.path.exists(FAISS_INDEX_PATH):
                self._index = faiss.read_index(FAISS_INDEX_PATH)
                self._initialized = True
                logging.info(f"Loaded existing vector index with {len(self.chunks)} chunks")
        except Exception as e:
            logging.error(f"Error loading vector index: {e}")
            self.chunks = []
            self.manifest = {}
            self._index = None

    def save(self):
        try:
            os.makedirs(INDEX_DIR, exist_ok=True)
            
            with open(MANIFEST_PATH, 'w') as f:
                json.dump(self.manifest, f)
            
            with open(METADATA_PATH, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            if self._index:
                faiss.write_index(self._index, FAISS_INDEX_PATH)
            
            logging.info(f"Saved vector index with {len(self.chunks)} chunks")
        except Exception as e:
            logging.error(f"Error saving vector index: {e}")

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
        current_files = {}
        for root, dirs, files in os.walk(self.directory):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                if file.endswith(('.py', '.md', '.txt', '.java', '.kt', '.ts', '.tsx', '.js')):
                    path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(path)
                        current_files[path] = mtime
                    except:
                        continue

        # Identify changes
        deleted_files = set(self.manifest.keys()) - set(current_files.keys())
        changed_files = {path for path, mtime in current_files.items() 
                         if path not in self.manifest or mtime > self.manifest.get(path, 0)}

        if not deleted_files and not changed_files:
            self._initialized = True
            return

        # Remove chunks for deleted or changed files
        files_to_remove = deleted_files | changed_files
        self.chunks = [c for c in self.chunks if c['path'] not in files_to_remove]

        # Re-index changed files
        for path in changed_files:
            try:
                if os.path.getsize(path) > 1024 * 1024:
                    continue
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        file_chunks = self._get_chunks(content, path)
                        if file_chunks:
                            texts = [c['text'] for c in file_chunks]
                            embeddings = embedder.encode(texts)
                            for chunk, emb in zip(file_chunks, embeddings):
                                chunk['embedding'] = emb
                                self.chunks.append(chunk)
                self.manifest[path] = current_files[path]
            except Exception as e:
                logging.error(f"Error indexing {path}: {e}")
                continue

        # Clean up manifest for deleted files
        for path in deleted_files:
            if path in self.manifest:
                del self.manifest[path]

        # Rebuild FAISS index
        if self.chunks:
            all_embeddings = np.array([c['embedding'] for c in self.chunks]).astype('float32')
            self._index = faiss.IndexFlatL2(all_embeddings.shape[1])
            self._index.add(all_embeddings)
        else:
            self._index = None

        self.save()
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
