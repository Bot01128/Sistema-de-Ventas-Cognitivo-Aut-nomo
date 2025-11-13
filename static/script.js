document.addEventListener('DOMContentLoaded', () => {

    // --- MANEJO DE LAS PESTAÑAS DEL DASHBOARD ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    // Función para mostrar la pestaña activa y ocultar las demás
    const switchTab = (activeButton) => {
        const tabId = activeButton.getAttribute('data-tab');
        const activeTabContent = document.getElementById(tabId);

        // Oculta todos los contenidos
        tabContents.forEach(content => content.style.display = 'none');
        // Muestra solo el activo
        if (activeTabContent) {
            activeTabContent.style.display = 'block';
        }

        // Actualiza el estado visual de los botones
        tabButtons.forEach(btn => btn.classList.remove('active'));
        activeButton.classList.add('active');
    };

    // Añade el evento click a cada botón
    tabButtons.forEach(button => {
        button.addEventListener('click', () => switchTab(button));
    });

    // Asegura que al cargar la página, solo se vea el contenido de la pestaña activa
    const initialActiveButton = document.querySelector('.tab-button.active');
    if (initialActiveButton) {
        switchTab(initialActiveButton);
    }

    // --- MANEJO DEL CHAT DE LA IA ---
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    if (chatForm) {
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

    function appendMessage(message, type) {
        const messageElement = document.createElement('p');
        messageElement.classList.add(type === 'user' ? 'msg-user' : 'msg-assistant');
        messageElement.innerText = message;
        if(chatMessages) {
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // --- LÓGICA DEL FORMULARIO DE CAMPAÑA (INTACTA) ---
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }
    
    // (Aquí iría el resto de la lógica de tu formulario si la tienes en este archivo)

});
