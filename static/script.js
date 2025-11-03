const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        tabContents.forEach(content => {
            content.style.display = content.id === tabId ? 'block' : 'none';
        });
    });
});

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
    let dailyCount = parseInt(prospectsInput.value) || 4;
    if (dailyCount < 4) { dailyCount = 4; prospectsInput.value = 4; }

    if (dailyCount >= 4 && dailyCount < 15) currentPlanKey = 'arrancador';
    else if (dailyCount >= 15 && dailyCount < 50) currentPlanKey = 'profesional';
    else currentPlanKey = 'dominador';
    
    const plan = plans[currentPlanKey];
    const extraProspects = dailyCount - plan.baseProspects;
    const finalCost = plan.basePrice + (extraProspects > 0 ? extraProspects * plan.pricePerExtra : 0);

    planCards.forEach(card => {
        card.classList.toggle('selected', card.dataset.plan === currentPlanKey);
    });

    selectedPlanEl.textContent = plan.name;
    dailyProspectsEl.textContent = dailyCount;
    totalCostEl.textContent = `$${finalCost.toFixed(2)}`;
}

prospectsInput.addEventListener('input', updateCosts);

planCards.forEach(card => {
    card.addEventListener('click', () => {
        const planKey = card.dataset.plan;
        prospectsInput.value = plans[planKey].baseProspects;
        updateCosts();
    });
});
updateCosts();

const descriptionTextarea = document.getElementById('product-description');
const charCountEl = document.getElementById('char-count');
if (descriptionTextarea) {
    descriptionTextarea.addEventListener('input', () => {
        const remaining = 1000 - descriptionTextarea.value.length;
        charCountEl.textContent = `${remaining} caracteres restantes`;
    });
}

const sendBtn = document.getElementById('send-btn');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
async function sendMessage() {
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
        const data = await response.json();
        addMessage(data.response, 'assistant');
    } catch (error) {
        addMessage('Lo siento, ocurrió un error.', 'assistant');
    }
}
function addMessage(text, sender) {
    const p = document.createElement('p');
    p.textContent = text;
    p.className = sender === 'user' ? 'msg-user' : 'msg-assistant';
    chatMessages.appendChild(p);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
if (sendBtn) sendBtn.addEventListener('click', sendMessage);
if (userInput) userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
