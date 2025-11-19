document.addEventListener('DOMContentLoaded', function() {

    // --- Controlador para el Chat de la IA ---
    const chatFormIA = document.getElementById('chat-form-ia');
    const userInputIA = document.getElementById('user-input-ia');
    const chatWindowIA = document.getElementById('chat-window-ia');

    if (chatFormIA) {
        const appendMessageIA = (message, sender) => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
            messageDiv.innerText = message;
            chatWindowIA.appendChild(messageDiv);
            chatWindowIA.scrollTop = chatWindowIA.scrollHeight;
        };

        chatFormIA.addEventListener('submit', async (event) => {
            event.preventDefault();
            const userMessage = userInputIA.value.trim();
            if (!userMessage) return;

            appendMessageIA(userMessage, 'user');
            userInputIA.value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage }),
                });
                if (!response.ok) throw new Error('La respuesta del servidor no fue OK');
                const data = await response.json();
                appendMessageIA(data.response, 'bot');
            } catch (error) {
                console.error('Error en el chat de IA:', error);
                appendMessageIA('Lo siento, estoy teniendo problemas de conexión.', 'bot');
            }
        });
    }

    // --- Controlador para el Chat con Humano ---
    const chatFormHuman = document.getElementById('chat-form-human');
    const userInputHuman = document.getElementById('user-input-human');
    const chatWindowHuman = document.getElementById('chat-window-human');

    if (chatFormHuman) {
        const appendMessageHuman = (message, sender) => {
            const messageDiv = document.createElement('div');
            // Nota: El mensaje del "humano" de soporte también usa 'bot-message' o un estilo similar del lado izquierdo.
            messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'human-message');
            messageDiv.innerText = message;
            chatWindowHuman.appendChild(messageDiv);
            chatWindowHuman.scrollTop = chatWindowHuman.scrollHeight;
        };

        chatFormHuman.addEventListener('submit', (event) => {
            event.preventDefault();
            const userMessage = userInputHuman.value.trim();
            if (!userMessage) return;
            
            appendMessageHuman(userMessage, 'user');
            userInputHuman.value = '';

            // Lógica de simulación para la respuesta del humano
            setTimeout(() => {
                appendMessageHuman("Gracias por tu mensaje. Uno de nuestros agentes te responderá a la brevedad.", 'human');
            }, 1000);
        });
    }
});
