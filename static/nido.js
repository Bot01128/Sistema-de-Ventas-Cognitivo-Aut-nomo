// Espera a que todo el contenido del HTML se cargue antes de ejecutar el script.
document.addEventListener('DOMContentLoaded', function() {

    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatWindow = document.getElementById('chat-window');

    // Si no encuentra el formulario del chat, no hace nada.
    if (!chatForm) return;

    // Función para añadir un mensaje a la ventana del chat
    function appendMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
        messageDiv.innerText = message;
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll hacia el final
    }

    // Función que se ejecuta al enviar el formulario
    async function handleChatSubmit(event) {
        event.preventDefault(); // Evita que la página se recargue
        const userMessage = userInput.value.trim();
        if (!userMessage) return; // No envía mensajes vacíos

        appendMessage(userMessage, 'user');
        userInput.value = ''; // Limpia el campo de entrada

        try {
            // Envía el mensaje del usuario al servidor (ruta /chat)
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) {
                throw new Error('La respuesta del servidor no fue OK');
            }

            const data = await response.json();
            appendMessage(data.response, 'bot'); // Añade la respuesta del bot

        } catch (error) {
            console.error('Error en el chat:', error);
            appendMessage('Lo siento, estoy teniendo problemas de conexión en este momento. Por favor, intenta de nuevo más tarde.', 'bot');
        }
    }

    // Asigna la función handleChatSubmit al evento 'submit' del formulario
    chatForm.addEventListener('submit', handleChatSubmit);
});
