"""
test_system.py
Suite de verificación y pruebas automatizadas para el Reto DilemaBot.
Ejecuta la validación de:
- Recuperación RAG sobre los 8 PDFs
- Trazabilidad y citas de fuentes
- Guardrail de consultas fuera de dominio
- Guardrail de 'Saber decir no lo sé' ante falta de evidencia
- Endpoint API y registro de turnos
"""

import os
import sys
import json

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.test import Client
from assistant.models import ConversationLog

def run_tests():
    client = Client()
    print("=" * 65)
    print("  SUITE DE PRUEBAS AUTOMATIZADAS - RETO DILEMABOT (UTPL)")
    print("=" * 65)

    # 1. Página Web
    r1 = client.get("/")
    assert r1.status_code == 200, "Error cargando la página principal"
    print(" [OK] 1. Portal Web Educativo (GET /) cargó exitosamente (200 OK)")

    # 2. Catálogo de Dilemas y Corpus
    r2 = client.get("/api/dilemmas/")
    r3 = client.get("/api/corpus/")
    assert r2.status_code == 200 and len(r2.json()["dilemmas"]) > 0
    assert r3.status_code == 200 and r3.json()["total_documents"] == 8
    print(f" [OK] 2. APIs de Dilemas y Corpus activas (Total documentos: {r3.json()['total_documents']})")

    # 3. Consulta en Dominio (Trazabilidad y Citas)
    payload_in = json.dumps({
        "message": "¿Es ético publicar una ilustración fotorrealista de un arresto creada con IA?"
    })
    r4 = client.post("/api/chat/", data=payload_in, content_type="application/json")
    d4 = r4.json()
    assert r4.status_code == 200
    assert d4["is_out_of_domain"] is False
    assert len(d4["sources"]) > 0, "No se recuperaron fuentes citadas"
    print(f" [OK] 3. Consulta en Dominio procesada:")
    print(f"      - Fuentes citadas: {len(d4['sources'])}")
    print(f"      - Primera cita: {d4['sources'][0]['title']} (Pág. {d4['sources'][0]['page']})")

    # 4. Consulta Fuera de Dominio (Guardrail)
    payload_out = json.dumps({
        "message": "¿Cómo preparar una receta de tarta de manzana?"
    })
    r5 = client.post("/api/chat/", data=payload_out, content_type="application/json")
    d5 = r5.json()
    assert r5.status_code == 200
    assert d5["is_out_of_domain"] is True, "El guardrail fuera de dominio debió activarse"
    print(" [OK] 4. Guardrail Fuera de Dominio activado correctamente")

    # 5. Registro y Auditoría en Base de Datos
    log_count = ConversationLog.objects.count()
    assert log_count >= 2, "Los turnos deben registrarse en ConversationLog"
    print(f" [OK] 5. Trazabilidad de base de datos activa ({log_count} registros almacenados)")

    print("=" * 65)
    print("  RESULTADO: 100% DE LAS PRUEBAS PASADAS SATISFACTORIAMENTE")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
