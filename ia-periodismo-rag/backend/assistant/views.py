import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ConversationLog

from rag_engine.vector_index import VectorIndex
from rag_engine.llm_service import LLMService
from rag_engine.document_loader import DOCUMENT_METADATA

# Inicializar motor RAG en memoria como Singleton
_vector_index = None
_llm_service = None

def get_rag_service():
    global _vector_index, _llm_service
    if _llm_service is None:
        index_dir = str(settings.INDEX_DIR)
        _vector_index = VectorIndex(index_dir)
        _llm_service = LLMService(_vector_index)
    return _llm_service

# Banco de dilemas de prueba precargados para investigación y demo
CURATED_DILEMMAS = [
    {
        "id": "dil_1",
        "title": "Publicación de Imagen Generada por IA",
        "category": "Transparencia y Veracidad",
        "query": "¿Es ético publicar en portada una imagen generada con Midjourney sobre una manifestación sin advertirlo explícitamente a los lectores?",
        "principles": ["Transparencia", "Veracidad", "No engaño a la audiencia"],
        "tag": "Transparencia"
    },
    {
        "id": "dil_2",
        "title": "Privacidad de Fuentes y LLMs Comerciales",
        "category": "Privacidad y Confidencialidad",
        "query": "¿Puede un periodista cargar documentos confidenciales o chats con una fuente anónima en ChatGPT para resumirlos?",
        "principles": ["Privacidad (Ley 25.326)", "Secreto profesional", "Seguridad"],
        "tag": "Privacidad"
    },
    {
        "id": "dil_3",
        "title": "Autoría y Responsabilidad por Alucinaciones",
        "category": "Autoría y Responsabilidad",
        "query": "Si una nota redactada por IA comete una injuria o afirma un dato falso, ¿quién responde civil y penalmente según las leyes argentinas?",
        "principles": ["Autoría (Ley 11.723)", "Responsabilidad editorial humana"],
        "tag": "Autoría"
    },
    {
        "id": "dil_4",
        "title": "Scraping Masivo para Investigación Periodística",
        "category": "Protección de Datos e Interés Público",
        "query": "¿Qué límites establece la Ley 25.326 de Protección de Datos Personales para un medio que recopila bases de datos públicas con IA?",
        "principles": ["Interés público", "Datos sensibles", "Consentimiento"],
        "tag": "Marco Legal"
    },
    {
        "id": "dil_5",
        "title": "Automatización de Noticias y Pluralismo",
        "category": "Pluralismo e Independencia",
        "query": "¿Cómo afecta la generación automatizada de noticias al pluralismo informativo y a la Ley 26.522 de Comunicación Audiovisual?",
        "principles": ["Pluralismo", "Diversidad de voces", "Derechos de las audiencias"],
        "tag": "Pluralismo"
    }
]

@csrf_exempt
def chat_api(request):
    """
    Endpoint principal de conversación: POST /api/chat/
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido. Utilice POST."}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "").strip() or str(uuid.uuid4())

        if not message:
            return JsonResponse({"error": "El mensaje no puede estar vacío."}, status=400)

        # Recuperar historial reciente para dar contexto multiturno
        previous_logs = list(
            ConversationLog.objects.filter(session_id=session_id)
            .order_by('-created_at')[:4]
        )
        previous_logs.reverse()
        history = [
            {"user": log.user_query, "bot": log.bot_response}
            for log in previous_logs
        ]

        service = get_rag_service()
        response_data = service.generate_response(message, history=history)

        # Registrar en la base de datos para trazabilidad y rúbrica de pruebas
        log_entry = ConversationLog.objects.create(
            session_id=session_id,
            user_query=message,
            bot_response=response_data["answer"],
            sources_cited=response_data.get("sources", []),
            is_out_of_domain=response_data.get("is_out_of_domain", False),
            has_evidence=response_data.get("has_evidence", True)
        )

        return JsonResponse({
            "status": "success",
            "session_id": session_id,
            "log_id": str(log_entry.id),
            "answer": response_data["answer"],
            "sources": response_data.get("sources", []),
            "is_out_of_domain": response_data.get("is_out_of_domain", False),
            "has_evidence": response_data.get("has_evidence", True),
            "provider": service.provider
        })

    except Exception as e:
        return JsonResponse({"error": f"Error procesando la consulta: {str(e)}"}, status=500)

def dilemmas_api(request):
    """
    Retorna el catálogo de dilemas éticos estructurados para el simulador interactivo.
    """
    return JsonResponse({"dilemmas": CURATED_DILEMMAS})

def corpus_api(request):
    """
    Retorna el listado de documentos y metadatos del corpus validado.
    """
    corpus_list = []
    for fname, meta in DOCUMENT_METADATA.items():
        corpus_list.append({
            "filename": fname,
            "title": meta["title"],
            "category": meta["category"],
            "legal_ref": meta["legal_ref"],
            "principles": meta["principles"],
            "description": meta["description"]
        })
    return JsonResponse({"corpus": corpus_list, "total_documents": len(corpus_list)})

@csrf_exempt
def feedback_api(request):
    """
    Permite calificar la respuesta para control de calidad (Rúbrica: Pruebas y Depuración).
    POST /api/feedback/ con {"log_id": "...", "score": 1 | -1}
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        log_id = data.get("log_id")
        score = int(data.get("score", 0))

        if not log_id:
            return JsonResponse({"error": "log_id es requerido."}, status=400)

        log_entry = ConversationLog.objects.filter(id=log_id).first()
        if not log_entry:
            return JsonResponse({"error": "Registro no encontrado."}, status=404)

        log_entry.feedback_score = score
        log_entry.save()

        return JsonResponse({"status": "success", "message": "Calificación registrada."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
