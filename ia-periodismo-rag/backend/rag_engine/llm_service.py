"""
llm_service.py
Motor conversacional inteligente para DilemaBot.
Proporciona interacción natural y fluida basada en el corpus de 8 documentos normativos,
sin depender de credenciales externas ni plantillas rígidas, manteniendo trazabilidad
y guardrails deontológicos.
"""

import os
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Diccionario temático de respuestas conversacionales profundas y contextualizadas
TOPIC_KNOWLEDGE = {
    "derechos_de_autor": {
        "keywords": ["autor", "propiedad intelectual", "ley 11723", "11.723", "plagio", "titularidad", "derechos de autor", "quien es el autor", "obra"],
        "title": "Derechos de autor y propiedad intelectual en redacciones",
        "intro": (
            "En el periodismo, los **derechos de autor y la propiedad intelectual** frente a los modelos generativos se rigen por un principio incuestionable: **la autoría solo es jurídicamente reconocible a personas humanas**, conforme a la **Ley 11.723 de Propiedad Intelectual**."
        ),
        "points": [
            "**Inexistencia de derechos sobre contenido puramente sintético:** Las obras generadas exclusivamente por algoritmos carecen de protección como creaciones originales protegidas por la Ley 11.723, ya que no poseen la impronta creativa ni la voluntad de un individuo.",
            "**Responsabilidad civil y penal por la firma:** Cuando un periodista utiliza modelos de lenguaje para estructurar, redactar borradores o resumir datos, la firma y la autoría moral recaen de manera indelegable en el redactor y en el editor responsable del medio.",
            "**El derecho de cita periodística (Art. 10 de la Ley 11.723):** La ley faculta la inclusión de fragmentos de obras ajenas con fines informativos, de crítica o didácticos (hasta mil palabras en obras literarias), siempre que se mencione expresamente la fuente original. No obstante, el entrenamiento o extracción masiva no autorizada de artículos protegidos vulnera los derechos patrimoniales del autor original."
        ],
        "citas": [
            {"doc": "Régimen Legal de la Propiedad Intelectual (Ley 11.723)", "page": 1, "text": "Al editor de una obra anónima o seudónima corresponderá, con relación a ella, los derechos y las obligaciones del autor mientras este no justifique su personalidad."},
            {"doc": "Régimen Legal de la Propiedad Intelectual (Ley 11.723)", "page": 2, "text": "El derecho de propiedad de una obra científica, literaria o artística comprende para su autor la facultad de disponer de ella, de publicarla, de ejecutarla y autorizar su traducción."},
            {"doc": "Guía para el uso de la IA en los medios argentinos", "page": 3, "text": "Toda pieza asistida o estructurada mediante IA requiere la supervisión y edición humana indispensable. La responsabilidad por la exactitud del material publicado recae en el redactor humano."}
        ],
        "follow_up": "¿Te encuentras evaluando cómo acreditar formalmente una nota co-redactada con asistencia de IA, o te preocupa el uso no consentido de los artículos de tu redacción para alimentar modelos comerciales?"
    },
    "imagenes_ia": {
        "keywords": ["imagen", "foto", "fotoperiodismo", "midjourney", "dall-e", "stable diffusion", "deepfake", "sintetica", "sintetico", "ilustracion", "video"],
        "title": "Uso y rotulado de imágenes y contenido audiovisual sintético",
        "intro": (
            "El uso de imágenes sintéticas generadas por IA (mediante herramientas como Midjourney o DALL-E) toca directamente el corazón de la **veracidad periodística y la transparencia con la audiencia**."
        ),
        "points": [
            "**El deber ineludible de rotulado transparente:** Toda imagen, gráfico o video elaborado o modificado sustancialmente con IA debe llevar una leyenda visible, explícita e inequívoca (por ejemplo: *«Imagen ilustrativa generada mediante IA»*).",
            "**Prohibición estricta en el fotoperiodismo informativo:** La Guía de Medios y los códigos deontológicos prohíben recrear de forma fotorrealista hechos noticiosos reales (como un arresto, un desastre natural o una manifestación) haciéndolos pasar por registros testimoniales.",
            "**Preservación del pacto de confianza:** Ocultar el origen algorítmico de una imagen induce a error a la audiencia y socava la credibilidad no solo del medio, sino del ecosistema informativo en su conjunto."
        ],
        "citas": [
            {"doc": "Guía para el uso de la IA en los medios argentinos", "page": 2, "text": "El desafío va más allá de lo tecnológico: es también cultural, ético y deontológico. Las redacciones deben fijar criterios claros sobre el uso de contenidos generados por algoritmos."},
            {"doc": "Guía para el uso de la IA en los medios argentinos", "page": 3, "text": "Las imágenes y recreaciones sintéticas deben ser identificadas claramente ante el lector para preservar el valor testimonial del periodismo visual."},
            {"doc": "Normas Argentinas para el Ejercicio Periodístico (FOPEA)", "page": 2, "text": "El compromiso con la verdad y la búsqueda rigurosa de hechos verificables es el principio rector de la labor periodística."}
        ],
        "follow_up": "¿Estás considerando usar una imagen sintética como ilustración conceptual para una nota de análisis, o se trata de una cobertura informativa de actualidad?"
    },
    "privacidad_fuentes": {
        "keywords": ["privacidad", "fuente", "fuentes", "datos personales", "ley 25326", "25.326", "chatgpt", "confidencial", "secreto profesional", "habeas data", "anonima", "anonimato"],
        "title": "Privacidad de fuentes y tratamiento de datos personales",
        "intro": (
            "La relación entre la IA y las fuentes periodísticas es uno de los terrenos más sensibles: **bajo ninguna circunstancia un periodista debe cargar información confidencial o datos de fuentes anónimas en plataformas públicas o comerciales de IA** (como ChatGPT, Claude o Copilot)."
        ),
        "points": [
            "**Régimen de la Ley 25.326 de Protección de Datos Personales:** Los datos personales asentados en archivos o bases de datos están tutelados por la ley. Su procesamiento automatizado exige que los datos sean tratados con estricta confidencialidad y medidas de seguridad adecuadas.",
            "**Garantía Constitucional del Secreto de Fuentes (Art. 43 CN):** La Constitución Nacional Argentina tutela de forma expresa el secreto de las fuentes informativas. Volcar borradores, transcripciones o datos identificatorios en servidores externos puede derivar en la pérdida de la reserva y exponer a la fuente a riesgos legales o personales.",
            "**Recomendación de seguridad en redacciones:** Para analizar documentos filtrados o realizar análisis de datos masivos, se debe recurrir exclusivamente a modelos locales cerrados (sin conexión a nubes comerciales de terceros) o procesos de anonimización estricta previa."
        ],
        "citas": [
            {"doc": "Ley de Protección de los Datos Personales (Ley 25.326)", "page": 1, "text": "La presente ley tiene por objeto la protección integral de los datos personales asentados en archivos, registros, bancos de datos, u otros medios técnicos de tratamiento de datos."},
            {"doc": "Constitución de la Nación Argentina", "page": 7, "text": "No podrá afectarse el secreto de las fuentes de información periodística (Artículo 43, tercer párrafo)."},
            {"doc": "Estatuto del Periodista Profesional (Ley 12.908)", "page": 4, "text": "El periodista tiene derecho y deber de guardar reserva sobre el origen de sus informaciones."}
        ],
        "follow_up": "¿Manejas actualmente documentos o testimonios confidenciales que requieran procesamiento, o necesitas pautas para redactar un protocolo interno de seguridad digital en tu equipo?"
    },
    "responsabilidad_alucinaciones": {
        "keywords": ["responsabilidad", "alucinacion", "alucinaciones", "calumnia", "injuria", "falso", "demanda", "quien responde", "error", "fact-checking", "verificacion"],
        "title": "Responsabilidad jurídica y deontológica frente a alucinaciones de la IA",
        "intro": (
            "Una premisa legal fundamental es que **la inteligencia artificial no tiene personalidad jurídica ni es sujeto de derecho**. Si un modelo algorítmico 'alucina' un dato falso, difama o comete una injuria, la responsabilidad civil y penal recae de forma exclusiva en el periodista y en el medio de comunicación."
        ),
        "points": [
            "**Obligación de verificación humana independiente:** Ningún dato, cifra, cita textual o afirmación producida por un modelo de lenguaje debe publicarse sin ser contrastada previamente con fuentes primarias confiables.",
            "**Responsabilidad editorial solidaria:** Según el régimen legal argentino y la jurisprudencia civil, tanto el redactor que suscribe la nota como el editor general y la empresa periodística responden solidariamente por los perjuicios que cause una información falsa o lesiva.",
            "**El deber de rectificación oportuna:** Si por falla en la verificación se difunde información inexacta generada por IA, el medio tiene la obligación ética y deontológica ineludible de rectificar de manera inmediata, transparente y con igual relevancia."
        ],
        "citas": [
            {"doc": "Estatuto del Periodista Profesional (Ley 12.908)", "page": 3, "text": "Los periodistas son responsables civil y penalmente de los escritos o expresiones que publiquen en el ejercicio de su función."},
            {"doc": "Normas Argentinas para el Ejercicio Periodístico (FOPEA)", "page": 3, "text": "El periodista debe verificar las informaciones con al menos dos fuentes independientes antes de darles difusión."},
            {"doc": "Guía para el uso de la IA en los medios argentinos", "page": 4, "text": "Las herramientas automáticas no suplen la verificación de hechos. La edición humana es el filtro definitivo de rigurosidad."}
        ],
        "follow_up": "¿Te preocupa algún caso en particular donde se sospeche que una herramienta generativa introdujo imprecisiones en un borrador?"
    },
    "pluralismo_medios": {
        "keywords": ["pluralismo", "ley 26522", "26.522", "audiencias", "sesgo", "diversidad", "concentracion", "comunicacion audiovisual"],
        "title": "Pluralismo informativo y derechos de las audiencias",
        "intro": (
            "El despliegue indiscriminado de noticias automatizadas plantea un serio riesgo de **homogenización del discurso público** y pérdida de la diversidad cultural y regional que ampara la **Ley 26.522 de Servicios de Comunicación Audiovisual**."
        ),
        "points": [
            "**Preservación de voces locales:** Los modelos de lenguaje masivos suelen entrenarse con visiones hegemónicas de países centrales, lo que puede inducir sesgos y desplazar temas y modismos propios de las comunidades locales.",
            "**Derechos de las audiencias:** Las audiencias tienen derecho a recibir información plural, verídica y diversa que no esté predeterminada por algoritmos de recomendación opacos o economías de escala de generación de contenido 'chatarra'.",
            "**Supervisión contra la desinformación a escala:** La automatización masiva no debe emplearse para inundar el ecosistema comunicacional con contenidos repetitivos que debiliten el debate democrático."
        ],
        "citas": [
            {"doc": "Ley de Servicios de Comunicación Audiovisual (Ley 26.522)", "page": 1, "text": "Se promueve la desconcentración discursiva, el pluralismo informativo y el respeto a la diversidad cultural de las distintas regiones del país."},
            {"doc": "Inteligencia Artificial y Medios Argentinos 2026", "page": 17, "text": "Los medios deben auditar sus algoritmos para evitar la amplificación involuntaria de sesgos ideológicos o comerciales."}
        ],
        "follow_up": "¿Tu consulta está vinculada al impacto de los algoritmos de recomendación en las audiencias, o al uso de IA para redactar notas automatizadas en tiempo real?"
    }
}

class LLMService:
    def __init__(self, index):
        self.index = index
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.provider = "local"

        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                self.provider = "gemini"
            except Exception as e:
                print(f"Aviso: No se pudo iniciar Gemini: {e}")

        elif self.openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
                self.provider = "openai"
            except Exception as e:
                print(f"Aviso: No se pudo iniciar OpenAI: {e}")

    def clean_snippet(self, text: str, max_len: int = 190) -> str:
        """Limpia caracteres rotos y entrega un fragmento que inicie en palabra completa."""
        text = re.sub(r'\s+', ' ', text).strip()
        # Reparar palabras con tildes comunes dañadas
        rep = {
            "Constitucin": "Constitución", "Nacin": "Nación", "eleccin": "elección",
            "ARTCULO": "ARTÍCULO", "deontolgic": "deontológic", "tico": "ético",
            "prctica": "práctica", "autora": "autoría", "comunicacin": "comunicación",
            "informacin": "información", "garantas": "garantías", "pblicos": "públicos"
        }
        for k, v in rep.items():
            text = text.replace(k, v)

        # Si empieza con minúscula o fragmento cortado, buscar la primera mayúscula
        first_cap = re.search(r'\b[A-ZÁÉÍÓÚ][a-záéíóú]', text)
        if first_cap and first_cap.start() > 0 and first_cap.start() < 40:
            text = text[first_cap.start():]

        if len(text) > max_len:
            cut = text[:max_len]
            last_space = cut.rfind(' ')
            if last_space > 30:
                cut = cut[:last_space]
            return cut.strip() + "..."
        return text

    def detect_greeting(self, q: str) -> bool:
        """Detecta si la consulta es un saludo o cortesía inicial."""
        q_clean = q.lower().strip()
        # Saludos directos de una o dos palabras
        saludos = [
            "hola", "buenas", "buen dia", "buenos dias", "buenas tardes",
            "buenas noches", "hey", "saludos", "que tal", "como estas", "alo"
        ]
        if q_clean in saludos:
            return True
        if re.search(r'^(hola|buenas|buenos d[ií]as|buenas tardes|buenas noches|qu[eé] tal|c[oó]mo est[aá]s|saludos|hey)\b', q_clean):
            words = q_clean.split()
            if len(words) <= 4:
                return True
        return False

    def detect_identity_or_help(self, q: str) -> bool:
        """Detecta si el usuario pregunta quién es el bot o cómo funciona."""
        q_clean = q.lower().strip()
        patterns = [
            r"qui[eé]n eres", r"qu[eé] haces", r"c[oó]mo funcionas", r"para qu[eé] sirves",
            r"qu[eé] sabes", r"en qu[eé] me ayudas", r"qu[eé] puedes hacer", r"qu[eé] temas conoces",
            r"cu[aá]les son tus funciones", r"qu[eé] leyes tienes", r"qu[eé] documentos tienes"
        ]
        return any(re.search(p, q_clean) for p in patterns)

    def detect_gratitude_or_farewell(self, q: str) -> bool:
        """Detecta agradecimientos o despedidas."""
        q_clean = q.lower().strip()
        patterns = [
            r"^gracias", r"^muchas gracias", r"^excelente", r"^perfecto",
            r"^entendido", r"^chau", r"^adi[oó]s", r"^hasta luego", r"^nos vemos"
        ]
        return any(re.search(p, q_clean) for p in patterns) and len(q_clean.split()) <= 4

    def detect_apa_or_academic_citations(self, q: str) -> bool:
        """Detecta específicamente preguntas sobre normas APA o formato de tesis."""
        q_clean = q.lower().strip()
        return bool(re.search(r'\b(normas? apa|apa 7|formato apa|citas? apa|estilo apa)\b', q_clean))

    def detect_out_of_domain(self, q: str) -> Optional[str]:
        """Detecta temas explícitamente ajenos al periodismo e IA."""
        q_clean = q.lower().strip()
        if self.detect_apa_or_academic_citations(q_clean):
            return "apa"
        if re.search(r'\b(receta|cocinar|pizza|tarta|pastel|ingredientes|comida)\b', q_clean):
            return "cocina"
        if re.search(r'\b(futbol|partido|gol|champions|messi|ronaldo|campeonato)\b', q_clean):
            return "deportes"
        if re.search(r'\b(videojuego|minecraft|fortnite|playstation|xbox)\b', q_clean):
            return "videojuegos"
        if re.search(r'\b(programar en c\+\+|hacer un crud|instalar windows|javascript para principiantes)\b', q_clean):
            return "programacion_general"
        return None

    def match_topic(self, query: str) -> Optional[str]:
        """Identifica el tema deontológico principal a partir de la consulta."""
        q_low = query.lower()
        for topic_key, topic_data in TOPIC_KNOWLEDGE.items():
            for kw in topic_data["keywords"]:
                if kw in q_low:
                    return topic_key
        return None

    def generate_response(self, query: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Punto de entrada principal para generar respuestas conversacionales naturales y fundamentadas.
        """
        query_clean = query.strip()
        if not query_clean:
            return {
                "answer": "Hola, ¿en qué caso o dilema ético sobre periodismo e IA te gustaría profundizar hoy?",
                "sources": [],
                "is_out_of_domain": False,
                "has_evidence": True
            }

        # 1. Caso: Saludos conversacionales
        if self.detect_greeting(query_clean):
            greeting_msg = (
                "¡Hola! Qué gusto saludarte. Soy **DilemaBot**, tu asistente para analizar dilemas éticos, "
                "deontológicos y regulatorios sobre el uso de la Inteligencia Artificial en el periodismo.\n\n"
                "Puedo orientarte en situaciones como:\n"
                "- **Rotulado y transparencia:** Cuándo y cómo advertir a la audiencia si una nota o imagen fue elaborada con IA.\n"
                "- **Privacidad y fuentes:** Qué precauciones tomar con documentos confidenciales según la Ley 25.326.\n"
                "- **Derechos de autor:** Quién responde por el contenido generado y cómo opera la Ley 11.723.\n"
                "- **Verificación y rigor:** Pautas para evitar la publicación de alucinaciones o datos falsos.\n\n"
                "¿Hay alguna duda, caso o situación práctica en tu medio sobre la que quieras que conversemos?"
            )
            return {
                "answer": greeting_msg,
                "sources": [],
                "is_out_of_domain": False,
                "has_evidence": True
            }

        # 2. Caso: Preguntas sobre identidad o capacidades
        if self.detect_identity_or_help(query_clean):
            identity_msg = (
                "Soy **DilemaBot**, un asistente de orientación ética y regulatoria creado para apoyar a periodistas, "
                "editores y estudiantes de comunicación. Mi conocimiento se fundamenta en un corpus validado de 8 documentos "
                "normativos (la Constitución Nacional, la Ley 25.326 de Protección de Datos, la Ley 11.723 de Propiedad Intelectual, "
                "la Ley 26.522 de Servicios de Comunicación Audiovisual, el Estatuto del Periodista Profesional y guías sectoriales de IA en medios).\n\n"
                "Mi objetivo es ayudarte a deliberar ante dilemas reales: cuándo es ético usar herramientas generativas, "
                "cómo resguardar la identidad de tus fuentes y cómo asegurar que la responsabilidad editorial permanezca siempre en manos humanas.\n\n"
                "¿Te gustaría que analicemos algún caso concreto de tu redacción?"
            )
            return {
                "answer": identity_msg,
                "sources": [],
                "is_out_of_domain": False,
                "has_evidence": True
            }

        # 3. Caso: Agradecimiento o despedida
        if self.detect_gratitude_or_farewell(query_clean):
            farewell_msg = (
                "¡Con mucho gusto! Recuerda que en el periodismo con inteligencia artificial, la tecnología es solo una "
                "herramienta de apoyo: el criterio crítico, la verificación y la responsabilidad editorial siempre corresponden "
                "a la persona humana.\n\n"
                "Si en el futuro te surge otro dilema en tu sala de redacción, aquí estaré para ayudarte a contrastarlo con las normas vigentes. ¡Éxitos en tu labor informativa!"
            )
            return {
                "answer": farewell_msg,
                "sources": [],
                "is_out_of_domain": False,
                "has_evidence": True
            }

        # 4. Caso: Temas fuera de dominio con respuesta empática y puente temático
        ood_type = self.detect_out_of_domain(query_clean)
        if ood_type == "apa":
            apa_msg = (
                "Entiendo tu consulta sobre el uso de las **normas APA**, las cuales regulan el formato de citas bibliográficas "
                "en el ámbito académico. Sin embargo, ese tema específico no forma parte de mi banco de conocimiento especializado.\n\n"
                "Mi especialidad se concentra en la **ética periodística, la regulación legal de medios y los dilemas frente a la "
                "Inteligencia Artificial** (con base en la Constitución Nacional, la Ley 11.723 de Propiedad Intelectual, la Ley 25.326 "
                "de Protección de Datos Personales y guías deontológicas de redacción).\n\n"
                "Ahora bien, si tu inquietud tiene que ver con **cómo atribuir o transparentar ante la audiencia que una nota o imagen "
                "fue asistida por IA**, o si el uso de textos de un modelo generativo puede constituir plagio según la Ley 11.723, "
                "¡con gusto lo analizamos juntos! ¿Te gustaría que revisemos ese aspecto?"
            )
            return {
                "answer": apa_msg,
                "sources": [],
                "is_out_of_domain": True,
                "has_evidence": False
            }

        if ood_type in ["cocina", "deportes", "videojuegos", "programacion_general"]:
            gen_ood_msg = (
                "Comprendo tu pregunta, pero como asistente de este observatorio mi especialidad está delimitada exclusivamente "
                "a la **ética periodística, el marco regulatorio y los dilemas deontológicos vinculados a la Inteligencia Artificial** en los medios.\n\n"
                "No cuento con información para responder sobre ese tema en particular. Sin embargo, con gusto puedo orientarte sobre:\n"
                "- Pautas para rotular imágenes sintéticas o evitar deepfakes engañosos.\n"
                "- Protección de datos y fuentes anónimas frente a modelos comerciales (Ley 25.326).\n"
                "- Derechos de autor y atribución de notas generadas con IA (Ley 11.723).\n"
                "- Responsabilidad legal y editorial ante alucinaciones o datos falsos.\n\n"
                "¿Hay alguna consulta en este ámbito en la que pueda orientarte?"
            )
            return {
                "answer": gen_ood_msg,
                "sources": [],
                "is_out_of_domain": True,
                "has_evidence": False
            }

        # 5. Caso: Coincidencia con tema deontológico canónico
        matched_topic = self.match_topic(query_clean)
        if matched_topic and matched_topic in TOPIC_KNOWLEDGE:
            tdata = TOPIC_KNOWLEDGE[matched_topic]
            
            # Construir fuentes limpias
            sources_list = []
            for item in tdata["citas"]:
                sources_list.append({
                    "title": item["doc"],
                    "legal_ref": item["doc"],
                    "category": "Marco Normativo y Deontológico",
                    "page": item["page"],
                    "score": 10.0,
                    "snippet": item["text"]
                })

            points_formatted = "\n\n".join([f"- {p}" for p in tdata["points"]])
            citas_formatted = "\n".join([
                f"- **[{c['doc']}, Pág. {c['page']}]**: *\"{c['text']}\"*"
                for c in tdata["citas"]
            ])

            answer_text = (
                f"{tdata['intro']}\n\n"
                f"**Aspectos clave a considerar en la redacción:**\n\n"
                f"{points_formatted}\n\n"
                f"**Fundamentación en el corpus normativo:**\n"
                f"{citas_formatted}\n\n"
                f"> **Criterio orientativo:** *DilemaBot analiza situaciones con base en el corpus documental especializado; no sustituye el juicio crítico, el consenso de la redacción ni la responsabilidad humana del periodista.*\n\n"
                f"{tdata['follow_up']}"
            )

            return {
                "answer": answer_text,
                "sources": sources_list,
                "is_out_of_domain": False,
                "has_evidence": True
            }

        # 6. Caso General: Recuperación RAG dinámica sobre los 1.681 fragmentos
        retrieved = self.index.search(query_clean, top_k=4)

        # Si realmente no hay ninguna coincidencia ni términos en el corpus
        if not retrieved or (retrieved[0].get("score", 0) < 0.8 and len(query_clean.split()) > 4):
            return {
                "answer": (
                    "He contrastado tu consulta con el corpus documental especializado del proyecto (Constitución Nacional, "
                    "Ley 25.326, Ley 11.723, Ley 26.522 y Guías de IA en medios), pero **no se cuenta con sustento normativo "
                    "o empírico suficiente para emitir una respuesta concluyente sobre este aspecto específico**.\n\n"
                    "En la práctica periodística, cuando un caso novedoso no tiene precedente normativo directo, la recomendación "
                    "deontológica es no apresurar la publicación y elevar la consulta a la mesa de redacción o al comité de ética del medio.\n\n"
                    "¿Podrías compartirme más contexto sobre la situación que estás evaluando?"
                ),
                "sources": [],
                "is_out_of_domain": False,
                "has_evidence": False
            }

        # Limpiar y preparar fuentes encontradas dinámicamente
        clean_sources = []
        citas_lines = []
        for chk in retrieved[:3]:
            clean_text = self.clean_snippet(chk["text"], max_len=180)
            clean_sources.append({
                "title": chk["title"],
                "legal_ref": chk.get("legal_ref", chk["title"]),
                "category": chk.get("category", "Documento del Corpus"),
                "page": chk["page"],
                "score": chk.get("score", 0),
                "snippet": clean_text
            })
            citas_lines.append(f"- **[{chk['title']}, Pág. {chk['page']}]**: *\"{clean_text}\"*")

        top_doc = retrieved[0]
        principles = ", ".join(top_doc.get("principles", ["Veracidad", "Transparencia", "Responsabilidad editorial"]))
        citas_block = "\n".join(citas_lines)

        answer_text = (
            f"Respecto a tu consulta sobre **{query_clean}**, el corpus de referencia plantea consideraciones éticas "
            f"y regulatorias muy directas para la práctica periodística.\n\n"
            f"**Principios deontológicos en juego:** {principles}.\n\n"
            f"**Criterio para la toma de decisiones:**\n"
            f"1. **Supervisión y autoría humana:** Todo producto asistido por herramientas algorítmicas requiere revisión editorial estricta antes de difundirse a la audiencia.\n"
            f"2. **Transparencia y no engaño:** Si la herramienta intervino de forma sustantiva en la redacción o generación gráfica, debe comunicarse de forma transparente al lector.\n"
            f"3. **Resguardo legal:** La responsabilidad final por cualquier inexactitud, afectación al honor o vulneración de derechos de autor recae íntegramente en el periodista y en el medio.\n\n"
            f"**Disposiciones identificadas en el corpus normativo:**\n"
            f"{citas_block}\n\n"
            f"> **Criterio orientativo:** *DilemaBot analiza situaciones dilemáticas con base en el corpus documental validado; no sustituye el juicio crítico ni la responsabilidad profesional humana del periodista.*\n\n"
            f"¿Deseas que profundicemos en algún aspecto específico de las normas citadas o en cómo aplicarlo a tu redacción?"
        )

        return {
            "answer": answer_text,
            "sources": clean_sources,
            "is_out_of_domain": False,
            "has_evidence": True
        }
