document.addEventListener('DOMContentLoaded', function() {
    // --- MÓDULO DE NAVEGACIÓN POR PESTAÑAS ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    function switchTab(tabId) {
        // Primero, ocultamos todo
        tabContents.forEach(content => {
            content.style.display = 'none';
        });
        // Luego, activamos el botón correcto
        tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });
        // Finalmente, mostramos solo el contenido deseado
        const activeContent = document.getElementById(tabId);
        if (activeContent) {
            activeContent.style.display = 'block';
        }
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });

    // --- CÓDIGO DEL CHAT (LO DEJAREMOS PARA DESPUÉS, PERO DEBE ESTAR) ---
    // (Aquí va tu lógica de chat original)

    // --- INICIALIZACIÓN ---
    // Al cargar la página, nos aseguramos de que solo la primera pestaña sea visible.
    switchTab('my-campaigns');
});
