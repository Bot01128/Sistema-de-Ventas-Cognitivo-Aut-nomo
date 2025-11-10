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

---

### Archivo `style.css` (Verdaderamente Completo)

```css
body, html { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; height: 100%; }
.top-bar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 10px 40px; border-bottom: 1px solid #ddd; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.user-info span { margin-right: 20px; color: #495057; }
.recharge-btn { background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: 600; }
.container { display: flex; height: calc(100% - 61px); }
.left-panel { flex: 0 0 450px; background-color: #ffffff; padding: 30px; display: flex; flex-direction: column; border-right: 1px solid #ddd; }
.right-panel { flex-grow: 1; background-color: #f8f9fa; padding: 40px; overflow-y: auto; }
h1, h2, h3, h4 { color: #1c1e21; margin-top: 0; }
.chat-header h2 { font-size: 24px; }
.chat-window { flex-grow: 1; border-radius: 8px; margin-top: 20px; display: flex; flex-direction: column; overflow: hidden; }
.chat-messages { flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; padding-right: 15px; }
.chat-messages::-webkit-scrollbar { width: 8px; }
.chat-messages::-webkit-scrollbar-track { background: #f1f1f1; }
.chat-messages::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
.chat-messages::-webkit-scrollbar-thumb:hover { background: #aaa; }
.chat-messages p { margin: 0; padding: 10px 15px; border-radius: 20px; max-width: 85%; word-wrap: break-word; line-height: 1.5; font-size: 15px;}
.msg-user { background-color: #007bff; color: white; align-self: flex-end; margin-left: auto; }
.msg-assistant { background-color: #e9ecef; color: #333; align-self: flex-start; }
.chat-input { display: flex; border-top: 1px solid #ddd; padding-top: 15px; margin-top: 15px; }
.chat-input input { flex-grow: 1; border: 1px solid #ccc; border-radius: 20px; padding: 10px 15px; font-size: 16px; outline: none; margin-right: 10px;}
.chat-input button { border: none; background: #007bff; color: white; padding: 10px 20px; cursor: pointer; font-size: 16px; border-radius: 20px; }
.tab-nav { display: flex; border-bottom: 1px solid #ddd; margin-bottom: 30px; }
.tab-nav button { background: none; border: none; padding: 15px 20px; cursor: pointer; font-size: 16px; color: #606770; border-bottom: 3px solid transparent; }
.tab-nav button.active { color: #007bff; border-bottom-color: #007bff; font-weight: 600; }
.form-section { margin-bottom: 25px; }
.form-section label { display: block; margin-bottom: 8px; font-weight: 600; color: #495057; }
.form-section input, textarea { width: 100%; padding: 12px; border: 1px solid #ced4da; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
.cta-button { background-color: #28a745; color: white; padding: 15px 25px; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 20px;}
.checkbox-group { display: flex; align-items: center; margin-bottom: 10px; }
.checkbox-group label { font-weight: normal; margin-left: 8px; }
.checkbox-group input { width: auto; }
textarea { resize: none; height: 150px; }
small { color: #6c757d; font-size: 12px; }
.campaign-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.campaign-table th, .campaign-table td { border: 1px solid #ddd; padding: 12px 15px; text-align: left; }
.campaign-table thead th { background-color: #f8f9fa; font-weight: 600; color: #495057; }
.campaign-table tbody tr:hover { background-color: #e9ecef; cursor: pointer; }
.plans-container { display: flex; gap: 20px; margin-bottom: 30px; }
.plan-card { flex: 1; border: 2px solid #ddd; border-radius: 8px; padding: 20px; text-align: center; cursor: pointer; transition: all 0.2s ease-in-out; }
.plan-card.selected { border-color: #007bff; box-shadow: 0 0 10px rgba(0, 123, 255, 0.5); transform: translateY(-5px); }
.plan-card h4 { margin: 0 0 10px 0; }
.plan-card .price { font-size: 24px; font-weight: bold; margin: 10px 0; }

/* --- ESTILOS MEJORADOS PARA EL BOTÓN "VIVO" (TÉCNICA CLÁSICA) --- */
#lancam {
    padding: 18px 30px;
    font-size: 20px;
    border-radius: 12px;
    margin-top: 30px;
    cursor: pointer;
    background-color: #28a745;
    color: white;
    font-weight: bold;
    transition: all 0.1s ease-in-out;
    border-style: solid;
    border-width: 4px;
    
    /* Estado por defecto "SOBRESALIDO" (outset) */
    border-top-color: #63d47a;
    border-left-color: #63d47a;
    border-bottom-color: #1c7430;
    border-right-color: #1c7430;
}

#lancam:hover {
    background-color: #2ebf4f;
}

#lancam:active {
    /* Estado al presionar "PLANO/HUNDIDO" (inset) */
    border-top-color: #1c7430;
    border-left-color: #1c7430;
    border-bottom-color: #63d47a;
    border-right-color: #63d47a;
    transform: translateY(1px);
}

/* --- ESTILOS PARA EL CAMPO DE TELÉFONO --- */
.iti {
    width: 100%;
}

@media (max-width: 900px) { 
    .container { flex-direction: column; overflow: auto; } 
    .left-panel { flex-basis: auto; min-height: 400px; } 
}
