document.addEventListener('DOMContentLoaded', function() {
    
    // --- MÓDULO DE NAVEGACIÓN POR PESTAÑAS ---
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
    const planCards = document.querySelectorAll('.plan-card');
    const prospectsInput = document.getElementById('prospects-per-day');
    const selectedPlanEl = document.getElementById('selected-plan');
    const dailyProspectsEl = document.getElementById('daily-prospects');
    const totalCostEl = document.getElementById('total-cost');
    const plans = {
        arrancador: { name: 'El Arrancador', basePrice: 149, baseProspects: 4, pricePerExtra: 30 },
        profesional: { name: 'El Profesional', basePrice: 399, baseProspects: 15, pricePerExtra: 27 },
        dominador: { name: 'El Dominador', basePrice: 999, baseProspects: 50, pricePerExtra: 20 }
    };
    let currentPlanKey = 'arrancador';
    function updateCosts() {
        if (!prospectsInput) return;
        let dailyCount = parseInt(prospectsInput.value) || 4;
        if (dailyCount < 4) { dailyCount = 4; prospectsInput.value = 4; }
        if (dailyCount >= 4 && dailyCount < 15) currentPlanKey = 'arrancador';
        else if (dailyCount >= 15 && dailyCount < 50) currentPlanKey = 'profesional';
        else currentPlanKey = 'dominador';
        const plan = plans[currentPlanKey];
        const extraProspects = dailyCount - plan.baseProspects;
        const finalCost = plan.basePrice + (extraProspects > 0 ? extraProspects * plan.pricePerExtra : 0);
        planCards.forEach(card => card.classList.toggle('selected', card.dataset.plan === currentPlanKey));
        if(selectedPlanEl) selectedPlanEl.textContent = plan.name;
        if(dailyProspectsEl) dailyProspectsEl.textContent = dailyCount;
        if(totalCostEl) totalCostEl.textContent = `$${finalCost.toFixed(2)}`;
    }
    if (prospectsInput) prospectsInput.addEventListener('input', updateCosts);
    planCards.forEach(card => {
        card.addEventListener('click', () => {
            const planKey = card.dataset.plan;
            if (prospectsInput) prospectsInput.value = plans[planKey].baseProspects;
            updateCosts();
        });
    });
    if (prospectsInput) updateCosts();

    // --- MÓDULO DEL CHAT MEJORADO ---
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    function addMessage(text, sender) {
        if(!chatMessages) return;
        const p = document.createElement('p');
        p.textContent = text;
        p.className = sender === 'user' ? 'msg-user' : 'msg-assistant';
        chatMessages.appendChild(p);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    async function handleSendMessage() {
        if (!userInput) return;
        const message = userInput.value.trim();
        if (!message) return;
        addMessage(message, 'user');
        userInput.value = '';
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: message })
            });
            if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);
            const data = await response.json();
            if (data.error) { addMessage(`Error: ${data.error}`, 'assistant'); } 
            else { addMessage(data.response, 'assistant'); }
        } catch (error) {
            console.error("Error en fetch del chat:", error);
            addMessage('Lo siento, ocurrió un error de conexión.', 'assistant');
        }
    }
    if (chatForm) {
        chatForm.addEventListener('submit', function(event) {
            event.preventDefault();
            handleSendMessage();
        });
    }
    
    // --- MÓDULO DE TELÉFONO INTERNACIONAL ---
    const phoneInputField = document.querySelector("#numero_whatsapp");
    if (phoneInputField) {
        window.intlTelInput(phoneInputField, {
            utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
            initialCountry: "auto",
            geoIpLookup: function(callback) {
                fetch('https://ipinfo.io/json') 
                .then(response => response.json())
                .then(data => callback(data.country))
                .catch(() => callback('us'));
            }
        });
    }

    // --- FUNCIONALIDAD PARA LA PESTAÑA DE SUGERENCIAS ---
    const sendSuggestionBtn = document.getElementById('send-suggestion-btn');
    const suggestionText = document.getElementById('suggestion-text');
    if (sendSuggestionBtn) {
        sendSuggestionBtn.addEventListener('click', () => {
            if (suggestionText && suggestionText.value.trim() !== '') {
                // Aquí puedes añadir la lógica para enviar la sugerencia al backend
                alert('¡Gracias! Tu sugerencia ha sido enviada directamente a nuestro equipo. ¡Eres increíble!');
                suggestionText.value = '';
            } else {
                alert('Por favor, escribe tu sugerencia antes de enviarla.');
            }
        });
    }

    // --- INICIALIZACIÓN ---
    switchTab('my-campaigns');
});```
