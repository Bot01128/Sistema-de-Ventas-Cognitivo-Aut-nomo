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
        if (initialActiveButton) {
            switchTab(initialActiveButton);
        }
    }

    // --- MANEJO DEL CHAT ---
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        // ... (código del chat sin cambios)
    }

    // --- LÓGICA DEL FORMULARIO DE CAMPAÑA ---
    const planCards = document.querySelectorAll('.plan-card');
    const prospectsInput = document.getElementById('prospects-per-day');
    const selectedPlanElement = document.getElementById('selected-plan');
    const dailyProspectsElement = document.getElementById('daily-prospects');
    const totalCostElement = document.getElementById('total-cost');
    
    if (planCards.length > 0 && prospectsInput && totalCostElement) {
        
        const plans = {
            arrancador: { name: 'El Arrancador', baseProspects: 4, baseCost: 149, extraCost: 37.25, limit: 14 },
            profesional: { name: 'El Profesional', baseProspects: 15, baseCost: 399, extraCost: 26.60, limit: 49 },
            dominador: { name: 'El Dominador', baseProspects: 50, baseCost: 999, extraCost: 20.00, limit: Infinity }
        };

        const handleFormUpdate = () => {
            // ... (código de cálculo de precios sin cambios)
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
    
    // --- LÓGICA PARA EL TELÉFONO ---
    const phoneInput = document.querySelector("#numero_whatsapp");
    if (phoneInput) {
        window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
    }
});
