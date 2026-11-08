from django.shortcuts import render
from assistant.views import CURATED_DILEMMAS
from rag_engine.document_loader import DOCUMENT_METADATA

ETHICAL_PILLARS = [
    {
        "id": "veracidad",
        "title": "Veracidad y No Alucinación",
        "icon": "shield-check",
        "summary": "Verificación rigurosa de hechos frente al riesgo de alucinación o invención de datos en modelos generativos.",
        "details": "Los algoritmos no comprenden la verdad empírica ni la deontología. El periodista debe contrastar toda afirmación automatizada con fuentes primarias y códigos de rigor.",
        "norm": "Código de Ética Periodística (FOPEA) & Estatuto Ley 12.908"
    },
    {
        "id": "transparencia",
        "title": "Transparencia con la Audiencia",
        "icon": "eye",
        "summary": "Deber inexcusable de advertir y rotular claramente cualquier contenido redactado, resumido o ilustrado con IA.",
        "details": "El lector tiene derecho a conocer el origen sintético de lo que consume. Se prohíbe presentar simulaciones o imágenes generadas como si fuesen capturas documentales reales.",
        "norm": "Guía para el uso de la IA en Medios (2026)"
    },
    {
        "id": "autoria",
        "title": "Autoría y Responsabilidad Humana",
        "icon": "pen-tool",
        "summary": "La firma, la autoría moral y la responsabilidad legal pertenecen únicamente a una persona humana.",
        "details": "Los sistemas de IA no son sujetos de derecho. Ante calumnias, difamaciones o infracciones, la responsabilidad civil y penal recae en el redactor y en el editor.",
        "norm": "Ley N° 11.723 de Propiedad Intelectual"
    },
    {
        "id": "privacidad",
        "title": "Privacidad y Secreto de Fuentes",
        "icon": "lock",
        "summary": "Protección absoluta de fuentes confidenciales y resguardo de datos personales en el procesamiento digital.",
        "details": "Está prohibido alimentar modelos de IA comerciales con datos sensibles de fuentes, borradores no publicados o información protegida por secreto profesional y hábeas data.",
        "norm": "Ley N° 25.326 & Art. 43 Constitución Nacional"
    },
    {
        "id": "independencia",
        "title": "Independencia Editorial y Sesgos",
        "icon": "scale",
        "summary": "Preservación del criterio propio frente a los sesgos y modelos propietarios de las corporaciones tecnológicas.",
        "details": "Los modelos de lenguaje reflejan visiones hegemónicas y sesgos de entrenamiento. La línea editorial debe auditar los sesgos algorítmicos para no subordinar su independencia.",
        "norm": "Cláusula de Conciencia & Estatuto del Periodista"
    },
    {
        "id": "pluralismo",
        "title": "Pluralismo y Diversidad",
        "icon": "users",
        "summary": "Garantía de representación de minorías, lenguajes locales y perspectivas diversas en la información.",
        "details": "Evitar la homogenización del discurso público generada por la automatización masiva. Fomentar el derecho a la información plural de todas las audiencias.",
        "norm": "Ley N° 26.522 de Comunicación Audiovisual"
    }
]

def home_view(request):
    """
    Vista principal de la página web del Observatorio y Portal DilemaBot.
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

    context = {
        "pillars": ETHICAL_PILLARS,
        "dilemmas": CURATED_DILEMMAS,
        "corpus": corpus_list,
        "total_docs": len(corpus_list)
    }
    return render(request, "portal/index.html", context)
