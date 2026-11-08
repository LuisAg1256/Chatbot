"""
document_loader.py
Carga, procesa y divide en fragmentos (chunks) los 8 PDFs del corpus sobre
ética, periodismo, IA y marco normativo.
"""

import os
import re
from typing import List, Dict, Any
import pypdf

# Mapeo descriptivo de metadatos por archivo
DOCUMENT_METADATA = {
    "1 constitucion_de_la_nacion_argentina.pdf": {
        "title": "Constitución de la Nación Argentina",
        "category": "Marco Constitucional y Derechos Fundamentales",
        "legal_ref": "Constitución Nacional Argentina",
        "principles": ["Libertad de expresión", "Acceso a la información", "Privacidad (Hábeas Data)", "Pluralismo"],
        "description": "Garantías constitucionales de libre emisión del pensamiento (Art. 14, 32), protección de fuentes y hábeas data (Art. 43)."
    },
    "11 IA y-medios-argentinos-2026.pdf": {
        "title": "Inteligencia Artificial y Medios Argentinos 2026",
        "category": "Estado del Arte e Investigación de Medios",
        "legal_ref": "Informe IA y Medios Argentinos",
        "principles": ["Transparencia algorítmica", "Independencia editorial", "Transformación digital"],
        "description": "Diagnóstico de la penetración, desafíos laborales y oportunidades de la IA en salas de redacción argentinas."
    },
    "12 guia-para-el-uso-de-la-ia-en-los-medios-argentinos.pdf": {
        "title": "Guía para el Uso de la IA en los Medios Argentinos",
        "category": "Directrices Deontológicas y Buenas Prácticas",
        "legal_ref": "Guía Deontológica de IA en Medios",
        "principles": ["Veracidad", "Transparencia", "Autoría responsable", "Supervisión humana"],
        "description": "Pautas éticas para periodistas y redacciones: rotulación de contenidos sintéticos, verificación y límites de la automatización."
    },
    "3 servicios-de-comunicacion-audiovisual-ley-26522.pdf": {
        "title": "Ley de Servicios de Comunicación Audiovisual (Ley 26.522)",
        "category": "Regulación de Medios y Pluralismo",
        "legal_ref": "Ley N° 26.522",
        "principles": ["Pluralismo", "Derechos de las audiencias", "Interés público", "Diversidad cultural"],
        "description": "Régimen de servicios audiovisuales, promoción del pluralismo informativo y protección de los derechos de los usuarios."
    },
    "4 ley11723.pdf": {
        "title": "Régimen Legal de la Propiedad Intelectual (Ley 11.723)",
        "category": "Propiedad Intelectual y Derechos de Autor",
        "legal_ref": "Ley N° 11.723",
        "principles": ["Autoría", "Propiedad intelectual", "Derecho moral", "Cita periodística"],
        "description": "Normativa sobre derechos de autor, uso de obras ajenas para entrenamiento o citación, y titularidad de creaciones originales."
    },
    "6 ley d eporteccion de datos arg_ley25326.pdf": {
        "title": "Ley de Protección de los Datos Personales (Ley 25.326)",
        "category": "Privacidad y Tratamiento de Información",
        "legal_ref": "Ley N° 25.326",
        "principles": ["Privacidad", "Consentimiento", "Protección de fuentes", "Seguridad de datos"],
        "description": "Protección integral de datos personales, límites al tratamiento algorítmico, perfilamiento y resguardo de la intimidad."
    },
    "7 trabajo periodistico.pdf": {
        "title": "Estatuto del Periodista Profesional (Ley 12.908)",
        "category": "Régimen Laboral y Profesional del Periodista",
        "legal_ref": "Estatuto del Periodista Profesional",
        "principles": ["Responsabilidad profesional", "Cláusula de conciencia", "Independencia"],
        "description": "Deberes, derechos y garantías laborales del periodista, cláusula de conciencia y responsabilidad sobre el material publicado."
    },
    "Normas argentinas ejercicio periodstico.pdf": {
        "title": "Normas Argentinas para el Ejercicio Periodístico (Código Ético)",
        "category": "Códigos Deontológicos Periodísticos",
        "legal_ref": "Código de Ética Periodística",
        "principles": ["Veracidad", "Rigor informativo", "Rectificación", "Separación hecho/opinión"],
        "description": "Principios éticos de la práctica periodística: honestidad intelectual, verificación de fuentes, respeto al honor y rectificación oportuna."
    }
}

class DocumentLoader:
    def __init__(self, pdfs_dir: str):
        self.pdfs_dir = pdfs_dir

    def clean_text(self, text: str) -> str:
        """Limpia saltos de línea excesivos y caracteres rotos de codificación."""
        if not text:
            return ""
        # Normalizar espacios y saltos de línea repetidos
        text = re.sub(r'\r\n|\r', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Limpiar caracteres ilegibles comunes
        text = text.replace('\x00', '').replace('\ufffd', '')
        return text.strip()

    def get_metadata_for_file(self, filename: str) -> Dict[str, Any]:
        """Obtiene metadatos normalizados por nombre de archivo."""
        for key, meta in DOCUMENT_METADATA.items():
            # Comparación flexible para evitar problemas con tildes o codificación
            clean_key = key.split('.')[0].lower()
            clean_fname = filename.split('.')[0].lower()
            if clean_key in clean_fname or clean_fname in clean_key:
                return meta
        return {
            "title": filename,
            "category": "Documento General",
            "legal_ref": filename,
            "principles": ["Ética general"],
            "description": "Documento de la base de conocimiento."
        }

    def load_and_chunk(self, chunk_size: int = 700, chunk_overlap: int = 120) -> List[Dict[str, Any]]:
        """
        Lee todos los PDFs, extrae el texto página por página y genera fragmentos (chunks)
        manteniendo la trazabilidad exacta (archivo, título, página, sección).
        """
        chunks = []
        chunk_id = 0

        if not os.path.exists(self.pdfs_dir):
            raise FileNotFoundError(f"El directorio de PDFs no existe: {self.pdfs_dir}")

        for fname in sorted(os.listdir(self.pdfs_dir)):
            if not fname.lower().endswith(".pdf"):
                continue

            fpath = os.path.join(self.pdfs_dir, fname)
            meta = self.get_metadata_for_file(fname)

            try:
                reader = pypdf.PdfReader(fpath)
                total_pages = len(reader.pages)

                for page_idx, page in enumerate(reader.pages):
                    raw_text = page.extract_text() or ""
                    cleaned = self.clean_text(raw_text)
                    if not cleaned or len(cleaned) < 40:
                        continue

                    # Dividir la página en chunks con solapamiento semántico
                    # Usar párrafos naturales si es posible
                    paragraphs = cleaned.split("\n\n")
                    current_chunk = ""

                    for p in paragraphs:
                        p = p.strip()
                        if not p:
                            continue

                        if len(current_chunk) + len(p) <= chunk_size:
                            current_chunk += ("\n\n" if current_chunk else "") + p
                        else:
                            if current_chunk:
                                chunk_id += 1
                                chunks.append({
                                    "id": f"chk_{chunk_id}",
                                    "text": current_chunk,
                                    "source_file": fname,
                                    "title": meta["title"],
                                    "category": meta["category"],
                                    "legal_ref": meta["legal_ref"],
                                    "page": page_idx + 1,
                                    "total_pages": total_pages,
                                    "principles": meta["principles"]
                                })
                            # Iniciar nuevo chunk con solapamiento si es largo
                            if len(p) > chunk_size:
                                # Dividir párrafo grande en segmentos
                                for i in range(0, len(p), chunk_size - chunk_overlap):
                                    sub_p = p[i:i + chunk_size]
                                    chunk_id += 1
                                    chunks.append({
                                        "id": f"chk_{chunk_id}",
                                        "text": sub_p,
                                        "source_file": fname,
                                        "title": meta["title"],
                                        "category": meta["category"],
                                        "legal_ref": meta["legal_ref"],
                                        "page": page_idx + 1,
                                        "total_pages": total_pages,
                                        "principles": meta["principles"]
                                    })
                                current_chunk = ""
                            else:
                                current_chunk = p

                    if current_chunk:
                        chunk_id += 1
                        chunks.append({
                            "id": f"chk_{chunk_id}",
                            "text": current_chunk,
                            "source_file": fname,
                            "title": meta["title"],
                            "category": meta["category"],
                            "legal_ref": meta["legal_ref"],
                            "page": page_idx + 1,
                            "total_pages": total_pages,
                            "principles": meta["principles"]
                        })

            except Exception as e:
                print(f"Error procesando {fname}: {e}")

        return chunks
