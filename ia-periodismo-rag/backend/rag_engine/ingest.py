"""
ingest.py
Script de ingesta y generación del índice vectorial para DilemaBot.
"""

import os
import sys
import warnings

# Suprimir advertencias de fuentes en PDFs
warnings.filterwarnings('ignore')

from rag_engine.document_loader import DocumentLoader
from rag_engine.vector_index import VectorIndex

def run_ingestion(pdfs_dir: str = None, index_dir: str = None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(base_dir)

    if not pdfs_dir:
        pdfs_dir = os.path.join(root_dir, "data", "pdfs")
    if not index_dir:
        index_dir = os.path.join(root_dir, "data", "index")

    print(f"=== INICIANDO INGESTA DEL CORPUS DILEMABOT ===")
    print(f"Directorio PDFs: {pdfs_dir}")
    print(f"Directorio Índice: {index_dir}")

    loader = DocumentLoader(pdfs_dir)
    chunks = loader.load_and_chunk(chunk_size=750, chunk_overlap=120)
    print(f"-> Total fragmentos (chunks) generados: {len(chunks)}")

    index = VectorIndex(index_dir)
    index.build_index(chunks)
    print(f"-> Índice construido y guardado con éxito en {index_dir}")

    # Prueba de recuperación
    test_query = "¿Es ético publicar una imagen generada con IA sin advertirlo?"
    print(f"\n--- PRUEBA DE RECUPERACIÓN ---")
    print(f"Pregunta: {test_query}")
    results = index.search(test_query, top_k=3)
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['title']} (Pág. {r['page']}, Score: {r['score']})")
        print(f"    Categoría: {r['category']}")
        print(f"    Texto: {r['text'][:140]}...")

    print("\n=== INGESTA COMPLETADA EXITOSAMENTE ===")

if __name__ == "__main__":
    run_ingestion()
