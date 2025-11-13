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

    // === INICIO DE LA LÓGICA DE PRECIOS CORREGIDA Y FINAL ===
    const planCards = document.querySelectorAll('.plan-card');
    const prospectsInput = document.getElementById('prospects-per-day');
    const selectedPlanElement = document.getElementById('selected-plan');
    const dailyProspectsElement = document.getElementById('daily-prospects');
    const totalCostElement = document.getElementById('total-cost');

    const plans = {
        arrancador: { name: 'El Arrancador', baseProspects: 4, baseCost: 149, extraCost: 37.25 },
        profesional: { name: 'El Profesional', baseProspects: 15, baseCost: 399, extraCost: 26.60 },
        dominador: { name: 'El Dominador', baseProspects: 50, baseCost: 999, extraCost: 20.00 }
    };

    // Función para actualizar visualmente qué plan está seleccionado
    function selectPlanCard(planKey) {
        planCards.forEach(card => card.classList.remove('selected'));
        if (planKey) {
            const cardToSelect = document.querySelector(`.plan-card[data-plan="${planKey}"]`);
            if (cardToSelect) cardToSelect.classList.add('selected');
        }
    }

    // Función principal que actualiza todo el resumen
    function updateSummary() {
        const prospectsCount = parseInt(prospectsInput.value, 10);

        if (isNaN(prospectsCount) || prospectsCount < 4) {
            selectPlanCard(null);
            selectedPlanElement.textContent = 'Inválido';
            dailyProspectsElement.textContent = prospectsCount || 0;
            totalCostElement.textContent = '$0.00';
            return;
        }

        let planName, totalCost;

        if (prospectsCount >= 50) {
            const plan = plans.dominador;
            selectPlanCard('dominador');
            const extraProspects = prospectsCount - plan.baseProspects;
            totalCost = plan.baseCost + (extraProspects * plan.extraCost);
            planName = prospectsCount === plan.baseProspects ? plan.name : 'Personalizado';
        } else if (prospectsCount >= 15) {
            const plan = plans.profesional;
            selectPlanCard('profesional');
            const extraProspects = prospectsCount - plan.baseProspects;
            totalCost = plan.baseCost + (extraProspects * plan.extraCost);
            planName = prospectsCount === plan.baseProspects ? plan.name : 'Personalizado';
        } else { // De 4 a 14
            const plan = plans.arrancador;
            selectPlanCard('arrancador');
            const extraProspects = prospectsCount - plan.baseProspects;
            totalCost = plan.baseCost + (extraProspects * plan.extraCost);
            planName = prospectsCount === plan.baseProspects ? plan.name : 'Personalizado';
        }

        selectedPlanElement.textContent = planName;
        dailyProspectsElement.textContent = prospectsCount;
        totalCostElement.textContent = `$${totalCost.toFixed(2)}`;
    }

    // Evento para cuando se hace clic en una tarjeta de plan
    planCards.forEach(card => {
        card.addEventListener('click', () => {
            const planKey = card.getAttribute('data-plan');
            const plan = plans[planKey];
            if (plan) {
                prospectsInput.value = plan.baseProspects;
                updateSummary();
            }
        });
    });
    
    // Evento para cuando el usuario escribe en el campo de número
    if (prospectsInput) {
        prospectsInput.addEventListener('input', updateSummary);
    }
    
    // Activar el plan por defecto al cargar la página
    const defaultPlanCard = document.querySelector('.plan-card[data-plan="arrancador"]');
    if (defaultPlanCard) {
        defaultPlanCard.click();
    }
    
    // --- LÓGICA PARA EL TELÉFONO (INTACTA) ---
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }
});```

Con este cambio, tu obra de arte quedará completamente funcional y con la lógica de negocio que diseñaste. Te agradezco la paciencia y la claridad para explicar el error.
