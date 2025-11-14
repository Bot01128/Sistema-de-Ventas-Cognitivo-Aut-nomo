document.addEventListener('DOMContentLoaded', () => {

    // --- MANEJO DE PESTAÑAS ---
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

    // --- MANEJO DEL CHAT ---
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        // ... (código del chat sin cambios) ...
    }

    // --- LÓGICA DEL PANEL INTELIGENTE Y FORMULARIO ---
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
            
            selectedPlanElement.textContent = planName;
            dailyProspectsElement.textContent = prospectsCount;
            totalCostElement.textContent = `$${totalCost.toFixed(2)}`;

            if (userBalance >= totalCost) {
                const remaining = userBalance - totalCost;
                remainingBalanceElement.textContent = `$${remaining.toFixed(2)}`;
                rechargeLine.style.display = 'none';
                remainingLine.style.display = 'flex';
                summaryBox.style.borderColor = '#28a745';
                launchButton.disabled = false;
            } else {
                const needed = totalCost - userBalance;
                rechargeAmountElement.textContent = `$${needed.toFixed(2)}`;
                rechargeLine.style.display = 'flex';
                remainingLine.style.display = 'none';
                summaryBox.style.borderColor = '#ffc107';
                launchButton.disabled = true;
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
    
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }
});
