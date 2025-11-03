document.addEventListener('DOMContentLoaded', function() {
    // Lógica de Pestañas
    const tabButtons = document.querySelectorAll('.tab-button');
    // ... (El resto de la lógica de pestañas) ...

    // Lógica del Chat
    const chatForm = document.getElementById('chat-form');
    // ... (El resto de la lógica del chat) ...

    // Lógica del Espía y Envío
    const lanzarBtn = document.getElementById('lanzar-campana-btn');
    if (lanzarBtn) {
        lanzarBtn.addEventListener('click', function(event) {
            event.preventDefault();
            // ... (La lógica completa de validación y fetch) ...
        });
    }
    // ... (El resto de tus funciones) ...

    // Inicialización
    switchTab('my-campaigns');
});
