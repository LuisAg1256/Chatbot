# Reto DilemaBot: Asistente Inteligente para el Análisis de Dilemas Éticos en Periodismo e IA

**Proyecto de Innovación Educativa UTPL (Periodo Octubre 2026 – Febrero 2027)**  
*Línea: Computación × Comunicación Social • Aprendizaje Basado en Retos (ABR)*

---

## 📌 1. Descripción del Proyecto

**DilemaBot** es un observatorio web y asistente conversacional basado en **Recuperación Aumentada por Generación (RAG)** diseñado para apoyar a periodistas, editores y estudiantes en el análisis de **dilemas éticos, deontológicos y jurídicos** vinculados al uso de la Inteligencia Artificial generativa en salas de redacción.

El sistema se fundamenta en un **corpus validado de 8 documentos normativos** (Constitución Nacional, Ley de Protección de Datos Personales, Ley de Propiedad Intelectual, Ley de Comunicación Audiovisual, Estatuto del Periodista Profesional y Guías de Buenas Prácticas de IA en Medios).

> ⚠️ **Premisa Deontológica Central:**  
> *"DilemaBot analiza dilemas y orienta con base en fuentes validadas; no sustituye el criterio, el juicio crítico ni la responsabilidad profesional humana del periodista."*  
> *"Un buen DilemaBot también sabe decir **«no lo sé»**: reconoce consultas fuera de su dominio y no inventa respuestas cuando falta evidencia."*

---

## 🏛️ 2. Los 6 Pilares Deontológicos del Portal

1. **Veracidad:** Verificación rigurosa de hechos frente al riesgo de alucinación algorítmica.
2. **Transparencia:** Deber de advertir a la audiencia cuándo un texto o imagen fue generado/asistido con IA.
3. **Autoría:** La autoría moral y la responsabilidad legal pertenecen exclusivamente a personas humanas (Ley 11.723).
4. **Privacidad:** Protección absoluta de fuentes anónimas y secreto profesional bajo la Ley 25.326.
5. **Independencia:** Auditoría de sesgos comerciales y preservación de la línea editorial propia.
6. **Pluralismo:** Diversidad de voces y protección de derechos de las audiencias (Ley 26.522).

---

## ⚙️ 3. Arquitectura Tecnológica

```
+-----------------------------------------------------------------------------------+
|                         FRONTEND & OBSERVATORIO WEB                               |
|  - Landing Page Editorial (Conceptos, 6 Pilares, Biblioteca de Leyes y Guías)     |
|  - Widget Flotante Conversacional (Chat multiturno, streaming, feedback, citas)   |
+-----------------------------------------------------------------------------------+
                                         │ (Fetch JSON)
                                         ▼
+-----------------------------------------------------------------------------------+
|                         BACKEND DJANGO (MVT + REST API)                           |
|  - App 'portal': Vistas públicas y renderizado de plantillas con Tailwind CSS     |
|  - App 'assistant': Endpoint POST /api/chat/, /api/dilemmas/, /api/feedback/      |
|  - App 'rag_engine': Motor de ingesta, índice semántico y control de guardrails   |
+-----------------------------------------------------------------------------------+
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
+------------------------------------+       +------------------------------------+
|       MOTOR RAG & INDEXACIÓN       |       |        GUARDRAILS & MODELO         |
| - 1.681 fragmentos semánticos      |       | - Guardrail Fuera de Dominio       |
| - BM25 híbrido + similitud coseno  |       | - Guardrail "Decir no lo sé"       |
| - Trazabilidad exacta de páginas   |       | - Gemini / OpenAI / Local Experto  |
+------------------------------------+       +------------------------------------+
```

---

## 📂 4. Estructura del Repositorio

```text
ia-periodismo-rag/
├── data/
│   ├── pdfs/                       # 8 PDFs del corpus normativo validado
│   └── index/                      # Índice semántico persistido (chunks + BM25)
│
├── backend/                        # Aplicación Web Django
│   ├── manage.py
│   ├── config/                     # Configuración central (settings, urls)
│   ├── portal/                     # App del portal y vistas educativas
│   │   ├── views.py
│   │   └── templates/portal/       # Plantilla principal y widget flotante
│   ├── assistant/                  # App de endpoints API y registro de turnos
│   │   ├── models.py               # Modelo ConversationLog (auditoría y feedback)
│   │   ├── views.py                # Controladores de chat, dilemas y corpus
│   │   └── urls.py
│   └── rag_engine/                 # Pipeline RAG
│       ├── document_loader.py      # Extracción y chunking semántico
│       ├── vector_index.py         # Motor de búsqueda vectorial y BM25
│       ├── llm_service.py          # Lógica analítica y guardrails
│       └── ingest.py               # Script de indexación
│
├── .env.example                    # Plantilla de variables de entorno
├── docker-compose.yml              # Configuración de PostgreSQL + pgvector
├── requirements.txt                # Dependencias Python
├── start.bat                       # Script de inicio rápido en Windows
└── test_system.py                  # Suite de pruebas automatizadas
```

---

## 🚀 5. Instrucciones de Instalación y Ejecución

### Requisitos Previos
* Python 3.11+ instalado.
* Git.

### Paso 1: Clonar y activar el entorno
```bash
cd ia-periodismo-rag
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate
```

### Paso 2: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Indexar el Corpus (Opcional, ya se encuentra preindexado)
```bash
cd backend
python -m rag_engine.ingest
```

### Paso 4: Iniciar el Servidor Django
```bash
python manage.py runserver 127.0.0.1:8000
```
O simplemente ejecuta en Windows:
```bash
start.bat
```

Abre tu navegador en: **`http://127.0.0.1:8000/`**

---

## 🧪 6. Ejecución de la Suite de Pruebas Automatizadas

Para validar todos los requerimientos de la rúbrica (trazabilidad de fuentes, guardrails fuera de dominio y base de datos):

```bash
python test_system.py
```

Salida esperada:
```text
=================================================================
  SUITE DE PRUEBAS AUTOMATIZADAS - RETO DILEMABOT (UTPL)
=================================================================
 [OK] 1. Portal Web Educativo (GET /) cargó exitosamente (200 OK)
 [OK] 2. APIs de Dilemas y Corpus activas (Total documentos: 8)
 [OK] 3. Consulta en Dominio procesada (Fuentes citadas: 4)
 [OK] 4. Guardrail Fuera de Dominio activado correctamente
 [OK] 5. Trazabilidad de base de datos activa
=================================================================
  RESULTADO: 100% DE LAS PRUEBAS PASADAS SATISFACTORIAMENTE
=================================================================
```

---

## 📊 7. Mapeo con la Rúbrica Oficial de Evaluación

| Criterio de la Rúbrica | Ponderación | Implementación en DilemaBot |
| :--- | :---: | :--- |
| **Funcionamiento técnico** | 20% | Django 5.x, API REST modular, persistencia SQLite/pgvector y renderizado rápido. |
| **Calidad y pertinencia de respuestas** | 20% | Formato estructurado en 4 niveles (Dilema, Principios, Normativa y Recomendación). |
| **Recuperación y trazabilidad** | 15% | Citas explícitas al documento, ley y número de página exacto con badge interactivo. |
| **Manejo fuera del dominio** | 10% | Clasificador de dominio que rechaza consultas ajenas cordialmente sin alucinar. |
| **Experiencia de usuario (UX)** | 10% | Landing page moderna con diseño editorial periodístico + widget flotante responsive. |
| **Arquitectura y calidad del código** | 10% | Separación en apps Django (`portal`, `assistant`, `rag_engine`), modularidad y tipado. |
| **Seguridad y uso responsable** | 5% | Modelo `ConversationLog` para trazabilidad y botones de retroalimentación de calidad. |
| **Documentación técnica** | 5% | Documentación exhaustiva en README, metadatos estructurados y suite de pruebas. |
| **Innovación de la propuesta** | 5% | Simulador de casos interactivo precargado que enlaza directamente con el widget. |
