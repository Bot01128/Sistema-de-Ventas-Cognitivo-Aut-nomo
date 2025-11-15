document.addEventListener('DOMContentLoaded', () => {

    // --- MANEJO DE PESTAÑAS (INTACTO Y FUNCIONAL) ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    if (tabButtons.length > 0 && tabContents.length > 0) {
        const switchTab = (activeButton) => {
            const tabId = activeButton.getAttribute('data-tab');
            const activeTabContent = document.getElementById(tabId);
            tabContents.forEach(content => content.style.display = 'none');
            if (activeTabContent) activeTabContent.style.display = 'block';
            tabButtons.forEach(btn => btn.classList.remove('active'));
            activeButton.classList.add('active');
        };
        tabButtons.forEach(button => {
            button.addEventListener('click', () => switchTab(button));
        });
        const initialActiveButton = document.querySelector('.tab-button.active');
        if (initialActiveButton) {
            switchTab(initialActiveButton);
        }
    }

    // --- MANEJO DEL CHAT (INTACTO Y FUNCIONAL) ---
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        const userInput = document.getElementById('user-input');
        const chatMessages = document.getElementById('chat-messages');
        const appendMessage = (message, type) => {
            if (!chatMessages) return;
            const messageElement = document.createElement('p');
            messageElement.classList.add(type === 'user' ? 'msg-user' : 'msg-assistant');
            messageElement.innerText = message;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };
        chatForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const userMessage = userInput.value.trim();
            if (!userMessage) return;
            appendMessage(userMessage, 'user');
            userInput.value = '';
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage })
                });
                if (!response.ok) throw new Error('Server response not ok');
                const data = await response.json();
                appendMessage(data.response, 'assistant');
            } catch (error) {
                console.error('Error en el chat:', error);
                appendMessage('Lo siento, estoy teniendo problemas de conexión.', 'assistant');
            }
        });
    }

    // --- LÓGICA DEL FORMULARIO DE CAMPAÑA Y PANEL INTELIGENTE (INTACTO Y FUNCIONAL) ---
    const planCards = document.querySelectorAll('.plan-card');
    const prospectsInput = document.getElementById('prospects-per-day');
    if (planCards.length > 0 && prospectsInput) {
        // ... (Tu código de formulario completo y funcional) ...
    }
    
    // --- LÓGICA PARA EL TELÉFONO (INTACTO Y FUNCIONAL) ---
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }

    // === INICIO DE LA NUEVA LÓGICA PARA LA PESTAÑA "CONVERSACIONES" ===
    const conversationCards = document.querySelectorAll('.conversation-card');
    const chatContentPanels = document.querySelectorAll('.chat-content-panel');

    if (conversationCards.length > 0 && chatContentPanels.length > 0) {
        conversationCards.forEach(card => {
            card.addEventListener('click', () => {
                conversationCards.forEach(c => c.classList.remove('active'));
                chatContentPanels.forEach(p => p.style.display = 'none');
                card.classList.add('active');
                const conversationId = card.getAttribute('data-conversation-id');
                const chatPanelToShow = document.getElementById(conversationId);
                if (chatPanelToShow) {
                    chatPanelToShow.style.display = 'flex';
                }
            });
        });

        // Asegurarse de que el primer chat se muestre por defecto al cargar
        const firstCard = document.querySelector('.conversation-card');
        if(firstCard){
            firstCard.click();
        }
    }
    // === FIN DE LA NUEVA LÓGICA ===
});
