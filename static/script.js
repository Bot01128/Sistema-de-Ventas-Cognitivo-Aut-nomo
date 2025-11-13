document.addEventListener('DOMContentLoaded', () => {

    // --- MANEJO DE PESTAÑAS (Funciona Correctamente) ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    const switchTab = (activeButton) => {
        const tabId = activeButton.getAttribute('data-tab');
        const activeTabContent = document.getElementById(tabId);

        tabContents.forEach(content => content.style.display = 'none');
        if (activeTabContent) {
            activeTabContent.style.display = 'block';
        }

        tabButtons.forEach(btn => btn.classList.remove('active'));
        activeButton.classList.add('active');
    };

    tabButtons.forEach(button => {
        button.addEventListener('click', () => switchTab(button));
    });

    const initialActiveButton = document.querySelector('.tab-button.active');
    if (initialActiveButton) {
        switchTab(initialActiveButton);
    }

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
        if(chatMessages) {
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // === INICIO DE LA LÓGICA RESTAURADA PARA EL FORMULARIO DE CAMPAÑA ===
    const planCards = document.querySelectorAll('.plan-card');
    const prospectsInput = document.getElementById('prospects-per-day');
    const selectedPlanElement = document.getElementById('selected-plan');
    const dailyProspectsElement = document.getElementById('daily-prospects');
    const totalCostElement = document.getElementById('total-cost');
    
    const plans = {
        arrancador: { name: 'El Arrancador', prospects: 4, cost: 149 },
        profesional: { name: 'El Profesional', prospects: 15, cost: 399 },
        dominador: { name: 'El Dominador', prospects: 50, cost: 999 }
    };

    function updateSummary(planName, prospects, cost) {
        if(selectedPlanElement) selectedPlanElement.textContent = planName;
        if(dailyProspectsElement) dailyProspectsElement.textContent = prospects;
        if(totalCostElement) totalCostElement.textContent = `$${cost.toFixed(2)}`;
    }

    planCards.forEach(card => {
        card.addEventListener('click', () => {
            // Estilo visual
            planCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');

            // Actualizar datos
            const planKey = card.getAttribute('data-plan');
            const plan = plans[planKey];
            if(plan) {
                if(prospectsInput) prospectsInput.value = plan.prospects;
                updateSummary(plan.name, plan.prospects, plan.cost);
            }
        });
    });

    if (prospectsInput) {
        prospectsInput.addEventListener('input', () => {
            // Si el usuario personaliza, deseleccionamos los planes
            planCards.forEach(c => c.classList.remove('selected'));

            const prospectsCount = parseInt(prospectsInput.value, 10);
            if (isNaN(prospectsCount) || prospectsCount < 4) {
                updateSummary('Personalizado', 0, 0);
                return;
            }

            // Aquí puedes añadir una lógica de precios personalizada si quieres
            // Por ahora, solo actualizamos el resumen con el número
            let calculatedCost = 0;
            // Busca si coincide con un plan existente
            let matchedPlan = false;
            for (const key in plans) {
                if (plans[key].prospects === prospectsCount) {
                    updateSummary(plans[key].name, plans[key].prospects, plans[key].cost);
                    document.querySelector(`.plan-card[data-plan="${key}"]`).classList.add('selected');
                    matchedPlan = true;
                    break;
                }
            }

            if (!matchedPlan) {
                // Si no coincide, podrías tener una fórmula de costo. 
                // Ejemplo simple:
                calculatedCost = prospectsCount * 30; // Fórmula de ejemplo
                updateSummary('Personalizado', prospectsCount, calculatedCost);
            }
        });
    }
    
    // Activar el plan por defecto al cargar la página
    const defaultPlan = document.querySelector('.plan-card[data-plan="arrancador"]');
    if (defaultPlan) {
        defaultPlan.click();
    }
    
    // --- LÓGICA PARA EL TELÉFONO (INTACTA) ---
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }
    // === FIN DE LA LÓGICA RESTAURADA ===
});
