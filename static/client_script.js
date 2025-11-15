document.addEventListener('DOMContentLoaded', () => {

    // --- MÓDULO 1: MANEJO DE PESTAÑAS (ROBUSTO) ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    if (tabButtons.length > 0 && tabContents.length > 0) {
        const switchTab = (activeButton) => {
            const tabId = activeButton.getAttribute('data-tab');
            const activeTabContent = document.getElementById(tabId);
            
            tabContents.forEach(content => { content.style.display = 'none'; });
            if (activeTabContent) { activeTabContent.style.display = 'block'; }
            
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
    }

    // --- MÓDULO 2: MANEJO DEL CHAT PRINCIPAL (ROBUSTO) ---
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

    // --- MÓDULO 3: LÓGICA DEL FORMULARIO DE CAMPAÑA (ROBUSTO) ---
    const createCampaignTab = document.getElementById('create-campaign');
    if (createCampaignTab) {
        const planCards = createCampaignTab.querySelectorAll('.plan-card');
        const prospectsInput = createCampaignTab.querySelector('#prospects-per-day');
        const selectedPlanElement = createCampaignTab.querySelector('#selected-plan');
        const dailyProspectsElement = createCampaignTab.querySelector('#daily-prospects');
        const totalCostElement = createCampaignTab.querySelector('#total-cost');
        const summaryBox = createCampaignTab.querySelector('#summary-box');
        const launchButton = createCampaignTab.querySelector('#lancam');
        const phoneInput = createCampaignTab.querySelector("#numero_whatsapp");
        
        if (planCards.length > 0 && prospectsInput) {
            const plans = {
                arrancador: { name: 'El Arrancador', baseProspects: 4, baseCost: 149, extraCost: 37.25, limit: 14 },
                profesional: { name: 'El Profesional', baseProspects: 15, baseCost: 399, extraCost: 26.60, limit: 49 },
                dominador: { name: 'El Dominador', baseProspects: 50, baseCost: 999, extraCost: 20.00, limit: Infinity }
            };

            const handleFormUpdate = () => {
                const prospectsCount = parseInt(prospectsInput.value, 10);
                if (isNaN(prospectsCount) || prospectsCount < 4) return;

                let activePlanKey;
                if (prospectsCount <= plans.arrancador.limit) { activePlanKey = 'arrancador'; } 
                else if (prospectsCount <= plans.profesional.limit) { activePlanKey = 'profesional'; } 
                else { activePlanKey = 'dominador'; }
                
                const currentPlan = plans[activePlanKey];
                planCards.forEach(card => card.classList.remove('selected'));
                const cardToSelect = createCampaignTab.querySelector(`.plan-card[data-plan="${activePlanKey}"]`);
                if (cardToSelect) cardToSelect.classList.add('selected');

                const extraProspects = prospectsCount - currentPlan.baseProspects;
                const totalCost = currentPlan.baseCost + (extraProspects * currentPlan.extraCost);
                const planName = (prospectsCount === currentPlan.baseProspects) ? currentPlan.name : 'Personalizado';
                
                if(selectedPlanElement) selectedPlanElement.textContent = planName;
                if(dailyProspectsElement) dailyProspectsElement.textContent = prospectsCount;
                if(totalCostElement) totalCostElement.textContent = `$${totalCost.toFixed(2)}`;
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

            const defaultPlanCard = createCampaignTab.querySelector('.plan-card[data-plan="arrancador"]');
            if (defaultPlanCard) {
                defaultPlanCard.click();
            }

            if (phoneInput) {
                window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
            }
        }
    }

    // --- MÓDULO 4: LÓGICA DE LA PESTAÑA "CONVERSACIONES" (ROBUSTO) ---
    const conversationsTab = document.getElementById('conversations');
    if (conversationsTab) {
        const conversationCards = conversationsTab.querySelectorAll('.conversation-card');
        const chatContentPanels = conversationsTab.querySelectorAll('.chat-content-panel');

        if (conversationCards.length > 0 && chatContentPanels.length > 0) {
            conversationCards.forEach(card => {
                card.addEventListener('click', () => {
                    conversationCards.forEach(c => c.classList.remove('active'));
                    chatContentPanels.forEach(p => p.style.display = 'none');
                    card.classList.add('active');
                    const conversationId = card.getAttribute('data-conversation-id');
                    const chatPanelToShow = conversationsTab.querySelector(`#${conversationId}`);
                    if (chatPanelToShow) {
                        chatPanelToShow.style.display = 'flex';
                    }
                });
            });

            const firstCard = conversationsTab.querySelector('.conversation-card');
            if (firstCard) {
                firstCard.click();
            }
        }
    }
});
