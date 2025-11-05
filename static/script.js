document.addEventListener('DOMContentLoaded', function() {
    // Lógica de Pestañas
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    function switchTab(tabId) {
        tabContents.forEach(content => { content.style.display = 'none'; });
        tabButtons.forEach(btn => btn.classList.remove('active'));
        document.getElementById(tabId)?.style.display = 'block';
        document.querySelector(`.tab-button[data-tab="${tabId}"]`)?.classList.add('active');
    }
    tabButtons.forEach(button => button.addEventListener('click', () => switchTab(button.dataset.tab)));

    // Lógica del Chat
    const chatForm = document.querySelector('.chat-input'); // Apuntamos al div
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    async function handleSendMessage(event) {
        event.preventDefault(); // ¡PREVENIMOS LA RECARGA AQUÍ!
        // ... (resto de tu lógica de sendMessage) ...
    }
    
    if (sendBtn) sendBtn.addEventListener('click', handleSendMessage);
    if (userInput) userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSendMessage(e);
        }
    });

    // Inicialización
    switchTab('my-campaigns');
});
