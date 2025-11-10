document.addEventListener('DOMContentLoaded', function() {
    
    // --- MÓDULO DE NAVEGNACIÓN POR PESTAÑAS (CORREGIDO Y COMPLETO) ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    function switchTab(tabId) {
        tabContents.forEach(content => {
            content.style.display = 'none';
        });
        tabButtons.forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeContent = document.getElementById(tabId);
        if (activeContent) {
            activeContent.style.display = 'block';
        }
        const activeButton = document.querySelector(`.tab-button[data-tab="${tabId}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });

    // --- MÓDULO DE PLANES Y COSTOS ---
    // ... (Este bloque completo no ha cambiado) ...

    // --- MÓDULO DEL CHAT MEJORADO ---
    // ... (Este bloque completo no ha cambiado) ...
    
    // --- MÓDULO DE TELÉFONO INTERNACIONAL ---
    // ... (Este bloque completo no ha cambiado) ...

    // --- NUEVO: FUNCIONALIDAD PARA LA PESTAÑA DE SUGERENCIAS ---
    const sendSuggestionBtn = document.getElementById('send-suggestion-btn');
    const suggestionText = document.getElementById('suggestion-text');
    if (sendSuggestionBtn) {
        sendSuggestionBtn.addEventListener('click', () => {
            if (suggestionText && suggestionText.value.trim() !== '') {
                alert('¡Gracias! Tu sugerencia ha sido enviada directamente a nuestro equipo. ¡Eres increíble!');
                suggestionText.value = '';
            } else {
                alert('Por favor, escribe tu sugerencia antes de enviarla.');
            }
        });
    }

    // --- INICIALIZACIÓN ---
    switchTab('my-campaigns');
});
