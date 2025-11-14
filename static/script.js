document.addEventListener('DOMContentLoaded', () => {

    // --- MANEJO DE PESTAÑAS (INTACTO) ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    if (tabButtons.length > 0 && tabContents.length > 0) {
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
    }

    // --- MANEJO DEL CHAT (INTACTO) ---
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        const userInput = document.getElementById('user-input');
        const chatMessages = document.getElementById('chat-messages');
        const appendMessage = (message, type) => {
            if (!chatMessages) return;
            const messageElement = document.createElement('p');
            messageElement.classList.add(type === 'user' ? 'msg-user' : 'msg-assistant');
            messageElement.innerText = message;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };
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

    // === INICIO DE LA LÓGICA DEL PANEL INTELIGENTE ===
    const planCards = document.querySelectorAll('.plan-card');
    const prospectsInput = document.getElementById('prospects-per-day');
    const selectedPlanElement = document.getElementById('selected-plan');
    const dailyProspectsElement = document.getElementById('daily-prospects');
    const totalCostElement = document.getElementById('total-cost');
    const currentBalanceElement = document.getElementById('current-balance');
    const rechargeLine = document.getElementById('recharge-line');
    const rechargeAmountElement = document.getElementById('recharge-amount');
    const remainingLine = document.getElementById('remaining-line');
    const remainingBalanceElement = document.getElementById('remaining-balance');
    const summaryBox = document.getElementById('summary-box');
    const launchButton = document.getElementById('lancam');
    const rechargeButton = document.getElementById('recarga-ya');
    
    if (planCards.length > 0 && prospectsInput && totalCostElement) {
        
        // Simulación del saldo del usuario. En el futuro, este valor vendrá del backend.
        const userBalance = 0.00; 
        if (currentBalanceElement) currentBalanceElement.textContent = `$${userBalance.toFixed(2)}`;

        const plans = {
            arrancador: { name: 'El Arrancador', baseProspects: 4, baseCost: 149, extraCost: 37.25, limit: 14 },
            profesional: { name: 'El Profesional', baseProspects: 15, baseCost: 399, extraCost: 26.60, limit: 49 },
            dominador: { name: 'El Dominador', baseProspects: 50, baseCost: 999, extraCost: 20.00, limit: Infinity }
        };

        const handleFormUpdate = () => {
            const prospectsCount = parseInt(prospectsInput.value, 10);
            if (isNaN(prospectsCount) || prospectsCount < 4) { return; }

            let activePlanKey;
            if (prospectsCount <= plans.arrancador.limit) { activePlanKey = 'arrancador'; } 
            else if (prospectsCount <= plans.profesional.limit) { activePlanKey = 'profesional'; } 
            else { activePlanKey = 'dominador'; }
            
            const currentPlan = plans[activePlanKey];
            planCards.forEach(card => card.classList.remove('selected'));
            const cardToSelect = document.querySelector(`.plan-card[data-plan="${activePlanKey}"]`);
            if (cardToSelect) cardToSelect.classList.add('selected');

            const extraProspects = prospectsCount - currentPlan.baseProspects;
            const totalCost = currentPlan.baseCost + (extraProspects * currentPlan.extraCost);
            const planName = (prospectsCount === currentPlan.baseProspects) ? currentPlan.name : 'Personalizado';
            
            // Actualizar resumen
            selectedPlanElement.textContent = planName;
            dailyProspectsElement.textContent = prospectsCount;
            totalCostElement.textContent = `$${totalCost.toFixed(2)}`;

            // Lógica del Panel Inteligente
            if (userBalance >= totalCost) {
                // El usuario tiene saldo suficiente
                const remaining = userBalance - totalCost;
                remainingBalanceElement.textContent = `$${remaining.toFixed(2)}`;
                rechargeLine.style.display = 'none';
                remainingLine.style.display = 'flex';
                summaryBox.style.borderColor = '#28a745'; // Borde verde
                launchButton.style.display = 'block';
                launchButton.disabled = false;
                rechargeButton.style.display = 'none';
            } else {
                // El usuario NO tiene saldo suficiente
                const needed = totalCost - userBalance;
                rechargeAmountElement.textContent = `$${needed.toFixed(2)}`;
                rechargeLine.style.display = 'flex';
                remainingLine.style.display = 'none';
                summaryBox.style.borderColor = '#ffc107'; // Borde amarillo/ámbar
                launchButton.style.display = 'block';
                launchButton.disabled = true; // Botón deshabilitado
                rechargeButton.style.display = 'none'; // Oculto por ahora, se puede cambiar a 'block'
            }
        };

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

        prospectsInput.addEventListener('input', handleFormUpdate);

        const defaultPlanCard = document.querySelector('.plan-card[data-plan="arrancador"]');
        if (defaultPlanCard) {
            defaultPlanCard.click();
        }
    }
    
    // --- LÓGICA PARA EL TELÉFONO (INTACTA) ---
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }
});
