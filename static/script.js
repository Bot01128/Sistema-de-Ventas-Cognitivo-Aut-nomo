document.addEventListener('DOMContentLoaded', () => {

    // --- MANEJO DE PESTAÑAS (Funciona Correctamente) ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    const switchTab = (activeButton) => {
        const tabId = activeButton.getAttribute('data-tab');
        const activeTabContent = document.getElementById(tabId);
        tabContents.forEach(content => content.style.display = 'none');
        if (activeTabContent) activeTabContent.style.display = 'block';
        tabButtons.forEach(btn => btn.classList.remove('active'));
        activeButton.classList.add('active');
    };

    tabButtons.forEach(button => {
        button.addEventListener('click', () => switchTab(button));
    });

    const initialActiveButton = document.querySelector('.tab-button.active');
    if (initialActiveButton) switchTab(initialActiveButton);

    // --- MANEJO DEL CHAT (Funciona Correctamente) ---
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
        if (chatMessages) {
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // === INICIO DE LA LÓGICA DE PRECIOS - VERSIÓN REFORZADA Y CORREGIDA ===
    const planCards = document.querySelectorAll('.plan-card');
    const prospectsInput = document.getElementById('prospects-per-day');
    const selectedPlanElement = document.getElementById('selected-plan');
    const dailyProspectsElement = document.getElementById('daily-prospects');
    const totalCostElement = document.getElementById('total-cost');

    // La base de datos de los planes con sus reglas de negocio
    const plans = {
        arrancador: { name: 'El Arrancador', baseProspects: 4, baseCost: 149, extraCost: 37.25, limit: 14 },
        profesional: { name: 'El Profesional', baseProspects: 15, baseCost: 399, extraCost: 26.60, limit: 49 },
        dominador: { name: 'El Dominador', baseProspects: 50, baseCost: 999, extraCost: 20.00, limit: Infinity }
    };

    // Función para actualizar el resumen final en la UI
    function updateSummaryUI(planName, prospects, cost) {
        if (selectedPlanElement) selectedPlanElement.textContent = planName;
        if (dailyProspectsElement) dailyProspectsElement.textContent = prospects;
        if (totalCostElement) totalCostElement.textContent = `$${cost.toFixed(2)}`;
    }

    // Función para actualizar el estilo visual de la tarjeta seleccionada
    function updateSelectedCardVisuals(planKey) {
        planCards.forEach(card => card.classList.remove('selected'));
        if (planKey) {
            const cardToSelect = document.querySelector(`.plan-card[data-plan="${planKey}"]`);
            if (cardToSelect) cardToSelect.classList.add('selected');
        }
    }

    // La función principal que se ejecuta cada vez que hay un cambio
    function handleFormUpdate() {
        const prospectsCount = parseInt(prospectsInput.value, 10);

        if (isNaN(prospectsCount) || prospectsCount < 4) {
            updateSelectedCardVisuals(null);
            updateSummaryUI('Inválido', prospectsCount || 0, 0);
            return;
        }

        let activePlanKey;
        let currentPlan;

        if (prospectsCount <= plans.arrancador.limit) { // De 4 a 14
            activePlanKey = 'arrancador';
        } else if (prospectsCount <= plans.profesional.limit) { // De 15 a 49
            activePlanKey = 'profesional';
        } else { // 50 o más
            activePlanKey = 'dominador';
        }
        
        currentPlan = plans[activePlanKey];
        updateSelectedCardVisuals(activePlanKey); // Mantiene la tarjeta correcta seleccionada

        const extraProspects = prospectsCount - currentPlan.baseProspects;
        const totalCost = currentPlan.baseCost + (extraProspects * currentPlan.extraCost);
        const planName = (prospectsCount === currentPlan.baseProspects) ? currentPlan.name : 'Personalizado';
        
        updateSummaryUI(planName, prospectsCount, totalCost);
    }

    // Asignar los eventos a los elementos
    planCards.forEach(card => {
        card.addEventListener('click', () => {
            const planKey = card.getAttribute('data-plan');
            const plan = plans[planKey];
            if (plan) {
                prospectsInput.value = plan.baseProspects;
                handleFormUpdate();
            }
        });
    });

    if (prospectsInput) {
        prospectsInput.addEventListener('input', handleFormUpdate);
    }

    // Cargar el estado inicial con el plan por defecto
    const defaultPlanCard = document.querySelector('.plan-card[data-plan="arrancador"]');
    if (defaultPlanCard) {
        defaultPlanCard.click();
    }
    
    // --- LÓGICA PARA EL TELÉFONO (INTACTA) ---
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }
});
