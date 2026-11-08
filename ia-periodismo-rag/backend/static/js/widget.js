/**
 * widget.js
 * Asistente conversacional para el Observatorio DilemaBot
 * Conexión asíncrona con el backend Django, trazabilidad de turnos y renderizado de citas documentales.
 */

(function () {
    const API_CHAT = '/api/chat/';
    const API_FEEDBACK = '/api/feedback/';

    let sessionId = localStorage.getItem('dilemabot_session_id');
    if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).substring(2, 12);
        localStorage.setItem('dilemabot_session_id', sessionId);
    }

    const widgetBtn = document.getElementById('dilemabot-toggle-btn');
    const widgetPanel = document.getElementById('dilemabot-panel');
    const closeBtn = document.getElementById('dilemabot-close-btn');
    const clearBtn = document.getElementById('dilemabot-clear-btn');
    const messagesContainer = document.getElementById('dilemabot-messages');
    const chatForm = document.getElementById('dilemabot-form');
    const chatInput = document.getElementById('dilemabot-input');
    const sendBtn = document.getElementById('dilemabot-send-btn');
    const typingIndicator = document.getElementById('dilemabot-typing');

    let isOpen = false;

    function toggleChat(forceOpen = null) {
        isOpen = forceOpen !== null ? forceOpen : !isOpen;
        if (isOpen) {
            widgetPanel.classList.remove('hidden', 'scale-95', 'opacity-0');
            widgetPanel.classList.add('flex', 'scale-100', 'opacity-100');
            chatInput.focus();
        } else {
            widgetPanel.classList.add('hidden', 'scale-95', 'opacity-0');
            widgetPanel.classList.remove('flex', 'scale-100', 'opacity-100');
        }
    }

    if (widgetBtn) widgetBtn.addEventListener('click', () => toggleChat());
    if (closeBtn) closeBtn.addEventListener('click', () => toggleChat(false));
    if (clearBtn) clearBtn.addEventListener('click', () => {
        messagesContainer.innerHTML = '';
        appendSystemGreeting();
    });

    window.openDilemaBotWithQuery = function (query) {
        toggleChat(true);
        if (query) {
            chatInput.value = query;
            sendMessage(query);
        }
    };

    const iconAssistant = `
        <div class="w-7 h-7 rounded-lg bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-blue-300 shrink-0">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
        </div>
    `;

    function appendSystemGreeting() {
        const greetingHtml = `
            <div class="flex items-start gap-3 my-3">
                ${iconAssistant}
                <div class="bg-slate-800 text-slate-100 rounded-2xl rounded-tl-sm p-4 text-xs sm:text-sm max-w-[85%] border border-slate-700 shadow-sm">
                    <div class="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-700/60">
                        <span class="font-semibold text-white tracking-tight">DilemaBot</span>
                        <span class="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">UTPL • RAG</span>
                    </div>
                    <p class="leading-relaxed text-slate-300">
                        Asistente técnico para el análisis de dilemas deontológicos y regulatorios de la IA en la labor informativa.
                    </p>
                    <div class="mt-3 text-xs bg-slate-900/80 p-2.5 rounded-lg border-l-2 border-amber-500 text-slate-300">
                        <span class="text-amber-400 font-semibold block text-[11px] mb-0.5">Nota de alcance:</span>
                        Herramienta de orientación fundamentada en fuentes; no sustituye la deliberación humana ni el criterio editorial de la redacción.
                    </div>
                    <div class="mt-3 pt-2.5 border-t border-slate-700/50">
                        <span class="text-[11px] text-slate-400 block mb-2 font-medium">Consultas frecuentes de referencia:</span>
                        <div class="flex flex-col gap-1.5">
                            <button class="chip-btn text-left text-[11px] bg-slate-900 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg transition border border-slate-700/80" data-query="¿Es ético publicar una imagen generada con IA sin advertirlo a la audiencia?">
                                <span class="text-blue-400 font-mono mr-1">01.</span> Rotulado de imágenes sintéticas en portada
                            </button>
                            <button class="chip-btn text-left text-[11px] bg-slate-900 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg transition border border-slate-700/80" data-query="¿Puede un periodista cargar documentos confidenciales o chats con una fuente anónima en ChatGPT?">
                                <span class="text-blue-400 font-mono mr-1">02.</span> Privacidad de fuentes y modelos comerciales
                            </button>
                            <button class="chip-btn text-left text-[11px] bg-slate-900 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg transition border border-slate-700/80" data-query="Si una nota redactada por IA comete una injuria, ¿quién responde según la ley argentina?">
                                <span class="text-blue-400 font-mono mr-1">03.</span> Responsabilidad legal por alucinaciones
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', greetingHtml);
        attachChipListeners();
    }

    function attachChipListeners() {
        document.querySelectorAll('.chip-btn').forEach(btn => {
            btn.onclick = (e) => {
                const target = e.currentTarget;
                const q = target.getAttribute('data-query');
                if (q) {
                    sendMessage(q);
                }
            };
        });
    }

    function parseMarkdown(text) {
        if (!text) return '';
        let escaped = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        escaped = escaped.replace(/^### (.*$)/gim, '<h4 class="font-semibold text-blue-300 mt-3 mb-1 text-xs uppercase tracking-wider border-b border-slate-700/50 pb-1">$1</h4>');
        escaped = escaped.replace(/^## (.*$)/gim, '<h3 class="font-bold text-white mt-3 mb-1 text-sm">$1</h3>');
        escaped = escaped.replace(/\*\*(.*?)\*\*/gim, '<strong class="text-white font-semibold">$1</strong>');
        escaped = escaped.replace(/\*(.*?)\*/gim, '<em class="text-slate-300">$1</em>');
        escaped = escaped.replace(/^> (.*$)/gim, '<blockquote class="border-l-2 border-slate-500 pl-3 py-1 my-2 text-xs italic text-slate-300 bg-slate-900/60 rounded-r">$1</blockquote>');
        escaped = escaped.replace(/^\- (.*$)/gim, '<li class="ml-4 list-disc text-slate-200 my-0.5">$1</li>');
        escaped = escaped.replace(/\n\n/g, '<p class="my-2"></p>');
        escaped = escaped.replace(/\n/g, '<br>');

        return escaped;
    }

    async function sendMessage(text) {
        if (!text || !text.trim()) return;
        const query = text.trim();
        chatInput.value = '';

        const userHtml = `
            <div class="flex items-start justify-end gap-3 my-3">
                <div class="bg-blue-600 text-white rounded-2xl rounded-tr-sm p-3.5 text-xs sm:text-sm max-w-[85%] shadow leading-relaxed font-normal">
                    ${query.replace(/</g, '&lt;').replace(/>/g, '&gt;')}
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', userHtml);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        typingIndicator.classList.remove('hidden');
        sendBtn.disabled = true;

        try {
            const res = await fetch(API_CHAT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: query, session_id: sessionId })
            });

            const data = await res.json();
            typingIndicator.classList.add('hidden');
            sendBtn.disabled = false;

            if (data.status === 'success') {
                renderBotResponse(data);
            } else {
                renderErrorMessage(data.error || 'Ocurrió un error al procesar la consulta.');
            }
        } catch (err) {
            typingIndicator.classList.add('hidden');
            sendBtn.disabled = false;
            renderErrorMessage('Error de comunicación con el servicio del observatorio.');
        }
    }

    function renderBotResponse(data) {
        const parsedText = parseMarkdown(data.answer);

        let sourcesHtml = '';
        if (data.sources && data.sources.length > 0) {
            const sourcePills = data.sources.map(s => `
                <div class="bg-slate-900 border border-slate-700/80 rounded-lg p-2.5 my-1.5 text-xs text-slate-300">
                    <div class="flex items-center justify-between text-blue-300 font-medium mb-1">
                        <span class="flex items-center gap-1.5 truncate">
                            <svg class="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                            ${s.title}
                        </span>
                        <span class="bg-slate-800 text-[10px] text-slate-400 px-2 py-0.5 rounded border border-slate-700 font-mono shrink-0 ml-2">Pág. ${s.page}</span>
                    </div>
                    <p class="text-[11px] text-slate-400 italic">"${s.snippet}"</p>
                </div>
            `).join('');

            sourcesHtml = `
                <div class="mt-3 pt-2.5 border-t border-slate-700/60">
                    <div class="flex items-center justify-between cursor-pointer text-xs font-medium text-slate-300 hover:text-white transition" onclick="this.nextElementSibling.classList.toggle('hidden')">
                        <span class="flex items-center gap-1.5">
                            <svg class="w-3.5 h-3.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                            </svg>
                            Fuentes documentales consultadas (${data.sources.length})
                        </span>
                        <span class="text-[10px] text-slate-400 font-mono">Desplegar</span>
                    </div>
                    <div class="sources-list mt-2">
                        ${sourcePills}
                    </div>
                </div>
            `;
        }

        const feedbackHtml = `
            <div class="flex items-center justify-between mt-3 pt-2 border-t border-slate-700/40 text-[11px] text-slate-400">
                <span class="text-[10px]">Evaluación de pertinencia:</span>
                <div class="flex items-center gap-1.5">
                    <button class="feedback-btn px-2 py-0.5 rounded bg-slate-900 border border-slate-700 hover:border-emerald-500 hover:text-emerald-400 transition text-[10px]" data-id="${data.log_id}" data-score="1">
                        Pertinente
                    </button>
                    <button class="feedback-btn px-2 py-0.5 rounded bg-slate-900 border border-slate-700 hover:border-rose-500 hover:text-rose-400 transition text-[10px]" data-id="${data.log_id}" data-score="-1">
                        Por ajustar
                    </button>
                </div>
            </div>
        `;

        const botHtml = `
            <div class="flex items-start gap-3 my-3">
                ${iconAssistant}
                <div class="bg-slate-800 text-slate-100 rounded-2xl rounded-tl-sm p-4 text-xs sm:text-sm max-w-[85%] border border-slate-700 shadow-sm">
                    <div class="leading-relaxed">
                        ${parsedText}
                    </div>
                    ${sourcesHtml}
                    ${feedbackHtml}
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', botHtml);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        document.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.onclick = async () => {
                const logId = btn.getAttribute('data-id');
                const score = btn.getAttribute('data-score');
                btn.parentElement.innerHTML = '<span class="text-slate-400 text-[10px]">Evaluación registrada</span>';
                try {
                    await fetch(API_FEEDBACK, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ log_id: logId, score: score })
                    });
                } catch (_) {}
            };
        });
    }

    function renderErrorMessage(msg) {
        const errorHtml = `
            <div class="flex items-start gap-3 my-3">
                <div class="w-7 h-7 rounded-lg bg-red-950 border border-red-800 text-red-400 flex items-center justify-center text-xs shrink-0 font-bold">
                    !
                </div>
                <div class="bg-red-950/30 text-red-200 border border-red-900/50 rounded-2xl p-3 text-xs max-w-[85%]">
                    ${msg}
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', errorHtml);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendMessage(chatInput.value);
        });
    }

    appendSystemGreeting();

})();
