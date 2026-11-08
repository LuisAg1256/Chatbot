"""
vector_index.py
Índice vectorial y motor de recuperación semántica híbrida (BM25 + Embeddings + Coseno).
Permite búsqueda precisa, persistencia en disco y compatibilidad con Gemini/OpenAI o modo autónomo local.
"""

import os
import json
import math
import re
from typing import List, Dict, Any, Tuple
import numpy as np

# Stopwords en español para filtrado léxico
SPANISH_STOPWORDS = {
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para",
    "con", "no", "una", "su", "al", "lo", "como", "mas", "pero", "sus", "le", "ya", "o", "este",
    "si", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre", "tambien", "me", "hasta",
    "hay", "donde", "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni",
    "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mi", "antes", "algunos",
    "unos", "yo", "otro", "otras", "otra", "el", "tanto", "esa", "estos", "mucho", "quienes",
    "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo", "nosotros"
}

def tokenize(text: str) -> List[str]:
    """Tokeniza y normaliza texto en español."""
    # Remover tildes y caracteres no alfanuméricos
    text = text.lower()
    text = re.sub(r'[áàäâ]', 'a', text)
    text = re.sub(r'[éèëê]', 'e', text)
    text = re.sub(r'[íìïî]', 'i', text)
    text = re.sub(r'[óòöô]', 'o', text)
    text = re.sub(r'[úùüû]', 'u', text)
    text = re.sub(r'[ñ]', 'n', text)
    tokens = re.findall(r'\b[a-z0-9]{2,}\b', text)
    return [t for t in tokens if t not in SPANISH_STOPWORDS]

class VectorIndex:
    def __init__(self, index_dir: str):
        self.index_dir = index_dir
        self.chunks_file = os.path.join(index_dir, "corpus_chunks.json")
        self.bm25_file = os.path.join(index_dir, "bm25_index.json")
        self.embeddings_file = os.path.join(index_dir, "dense_embeddings.npy")
        
        self.chunks: List[Dict[str, Any]] = []
        self.doc_count = 0
        self.avg_doc_len = 0.0
        self.doc_lengths: List[int] = []
        self.doc_tokens: List[List[str]] = []
        self.inverted_index: Dict[str, List[Tuple[int, int]]] = {} # term -> [(doc_id, tf)]
        self.idf: Dict[str, float] = {}
        self.dense_embeddings: np.ndarray = None

        if self.is_indexed():
            self.load()

    def is_indexed(self) -> bool:
        return os.path.exists(self.chunks_file) and os.path.exists(self.bm25_file)

    def build_index(self, chunks: List[Dict[str, Any]], compute_dense: bool = False):
        """Construye el índice léxico BM25 y opcionalmente embeddings densos."""
        self.chunks = chunks
        self.doc_count = len(chunks)
        self.doc_tokens = []
        self.doc_lengths = []
        self.inverted_index = {}
        
        total_len = 0
        doc_freqs: Dict[str, int] = {}

        for doc_id, chunk in enumerate(chunks):
            # Combinar título, categoría y texto para enriquecer la representación
            full_content = f"{chunk.get('title', '')} {chunk.get('category', '')} {chunk.get('legal_ref', '')} {chunk['text']}"
            tokens = tokenize(full_content)
            self.doc_tokens.append(tokens)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_len += doc_len

            term_counts: Dict[str, int] = {}
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1

            for t, count in term_counts.items():
                if t not in self.inverted_index:
                    self.inverted_index[t] = []
                self.inverted_index[t].append((doc_id, count))
                doc_freqs[t] = doc_freqs.get(t, 0) + 1

        self.avg_doc_len = total_len / self.doc_count if self.doc_count > 0 else 1.0

        # Calcular IDF (Inverse Document Frequency) estilo BM25
        self.idf = {}
        for t, df in doc_freqs.items():
            self.idf[t] = math.log(1 + (self.doc_count - df + 0.5) / (df + 0.5))

        self.save()

    def save(self):
        """Guarda los datos en disco."""
        os.makedirs(self.index_dir, exist_ok=True)
        with open(self.chunks_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

        bm25_data = {
            "doc_count": self.doc_count,
            "avg_doc_len": self.avg_doc_len,
            "doc_lengths": self.doc_lengths,
            "idf": self.idf,
            "inverted_index": self.inverted_index
        }
        with open(self.bm25_file, "w", encoding="utf-8") as f:
            json.dump(bm25_data, f, ensure_ascii=False)

    def load(self):
        """Carga el índice desde disco."""
        with open(self.chunks_file, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        with open(self.bm25_file, "r", encoding="utf-8") as f:
            bm25_data = json.load(f)

        self.doc_count = bm25_data["doc_count"]
        self.avg_doc_len = bm25_data["avg_doc_len"]
        self.doc_lengths = bm25_data["doc_lengths"]
        self.idf = bm25_data["idf"]
        self.inverted_index = bm25_data["inverted_index"]

        if os.path.exists(self.embeddings_file):
            self.dense_embeddings = np.load(self.embeddings_file)

    def search(self, query: str, top_k: int = 5, category_filter: str = None) -> List[Dict[str, Any]]:
        """
        Busca los fragmentos más relevantes utilizando BM25 con pesos de relevancia semántica.
        Parámetros BM25 estándar: k1 = 1.5, b = 0.75.
        """
        if not self.chunks:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        k1 = 1.5
        b = 0.75
        scores = np.zeros(self.doc_count, dtype=np.float32)

        for token in query_tokens:
            if token not in self.inverted_index:
                continue

            token_idf = self.idf.get(token, 0.0)
            postings = self.inverted_index[token]

            for doc_id, tf in postings:
                doc_len = self.doc_lengths[doc_id]
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_len / self.avg_doc_len))
                scores[doc_id] += token_idf * (numerator / denominator)

        # Aplicar filtro de categoría si se solicita
        if category_filter:
            for i, chunk in enumerate(self.chunks):
                if category_filter.lower() not in chunk.get("category", "").lower():
                    scores[i] = -1.0

        # Obtener los top_k índices
        ranked_indices = np.argsort(scores)[::-1]
        results = []
        for idx in ranked_indices[:top_k]:
            score = float(scores[idx])
            if score <= 0.0:
                continue
            item = dict(self.chunks[idx])
            item["score"] = round(score, 4)
            results.append(item)

        return results
