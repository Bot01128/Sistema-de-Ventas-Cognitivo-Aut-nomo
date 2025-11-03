document.addEventListener('DOMContentLoaded', function() {
    // --- LÓGICA DE PESTAÑAS ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    function switchTab(tabId) {
        tabButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tabId));
        tabContents.forEach(content => content.style.display = content.id === tabId ? 'block' : 'none');
    }
    tabButtons.forEach(button => button.addEventListener('click', () => switchTab(button.dataset.tab)));

    // --- LÓGICA DEL CHAT ---
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    function addMessage(text, sender) {
        if (!chatMessages) return;
        const p = document.createElement('p');
        p.textContent = text;
        p.className = sender === 'user' ? 'msg-user' : 'msg-assistant';
        chatMessages.insertBefore(p, chatMessages.firstChild);
    }
    async function handleSendMessage() {
        if (!userInput) return;
        const message = userInput.value.trim();
        if (!message) return;
        addMessage(message, 'user');
        userInput.value = '';
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: message })
            });
            if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);
            const data = await response.json();
            if (data.error) { addMessage(`Error: ${data.error}`, 'assistant'); }
            else { addMessage(data.response, 'assistant'); }
        } catch (error) {
            console.error("Error en fetch del chat:", error);
            addMessage('Lo siento, ocurrió un error de conexión.', 'assistant');
        }
    }
    if (chatForm) {
        chatForm.addEventListener('submit', function(event) {
            event.preventDefault();
            handleSendMessage();
        });
    }

    // --- LÓGICA DEL ESPÍA INTELIGENTE ---
    const lanzarBtn = document.getElementById('lanzar-campana-btn');
    if (lanzarBtn) {
        lanzarBtn.addEventListener('click', function(event) {
            event.preventDefault();
            clearAllErrors();
            // ... (Lógica de validación) ...
        });
    }
    function showError(element, message) { /* ... */ }
    function clearAllErrors() { /* ... */ }
    
    // --- INICIALIZACIÓN ---
    switchTab('my-campaigns');
});
