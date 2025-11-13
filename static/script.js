// Espera a que todo el contenido del HTML se cargue antes de ejecutar el script.
document.addEventListener('DOMContentLoaded', () => {

    // --- MANEJO DE LAS PESTAÑAS DEL DASHBOARD ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Quita la clase 'active' de todos los botones
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // Añade 'active' solo al botón clickeado
            button.classList.add('active');

            // Oculta todo el contenido
            tabContents.forEach(content => content.style.display = 'none');

            // Muestra solo el contenido asociado al botón clickeado
            const tabId = button.getAttribute('data-tab');
            const activeTabContent = document.getElementById(tabId);
            if (activeTabContent) {
                activeTabContent.style.display = 'block';
            }
        });
    });

    // --- MANEJO DEL CHAT DE LA IA ---
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');

    if (chatForm) {
        chatForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const userMessage = userInput.value.trim();
            if (!userMessage) return;

            // Muestra el mensaje del usuario
            appendMessage(userMessage, 'user');
            userInput.value = '';

            try {
                // Envía el mensaje al servidor
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage })
                });

                if (!response.ok) throw new Error('Server response not ok');
                
                const data = await response.json();
                // Muestra la respuesta del bot
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
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- LÓGICA DEL FORMULARIO DE CAMPAÑA (INTACTA) ---
    // (Aquí va toda la lógica de los planes, cálculo de costos, etc. Se queda igual)
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }
    
    // (El resto de tu lógica de formulario se mantiene)
});
