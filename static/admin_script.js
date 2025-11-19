document.addEventListener('DOMContentLoaded', () => {

    // --- MÓDULO DE PESTAÑAS ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    if (tabButtons.length > 0 && tabContents.length > 0) {
        const switchTab = (activeButton) => {
            if (!activeButton) return;
            const tabId = activeButton.getAttribute('data-tab');
            const activeTabContent = document.getElementById(tabId);
            tabContents.forEach(content => { content.style.display = 'none'; });
            if (activeTabContent) { activeTabContent.style.display = 'block'; }
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

    // --- MÓDULO DEL CHAT DE "DIOS" ---
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        const userInput = document.getElementById('user-input');
        const chatMessages = document.getElementById('chat-messages');
        const appendMessage = (message, type) => {
            if (!chatMessages) return;
            const messageElement = document.createElement('p');
            messageElement.classList.add(type === 'user' ? 'msg-user' : 'msg-assistant');
            messageElement.innerHTML = message; // Usamos innerHTML para poder formatear la respuesta
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };
        
        chatForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const userMessage = userInput.value.trim();
            if (!userMessage) return;
            
            appendMessage(userMessage, 'user');
            userInput.value = '';

            // --- SIMULACIÓN DE RESPUESTA DEL ASISTENTE DE CEO ---
            // En el futuro, esto hará una llamada a un endpoint /admin-chat
            let botResponse = "Comando no reconocido. Intenta con 'Muéstrame clientes por consumo'.";
            if (userMessage.toLowerCase().includes("clientes por consumo")) {
                botResponse = "Claro. Aquí está el top 3:<br>1. Ferretería El Tornillo Feliz ($12.50)<br>2. Spas de Lujo S.A. ($9.80)<br>3. Zapatería Veloz ($4.50)";
            } else if (userMessage.toLowerCase().includes("nuevos registros")) {
                botResponse = "Hay 2 nuevos registros: 'Restaurante Sabor Divino' y 'Clínica Dental Sonrisa Perfecta'.";
            }
            
            setTimeout(() => {
                appendMessage(botResponse, 'assistant');
            }, 500);
        });
    }
});
