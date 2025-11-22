// --- CONFIGURACIÓN DE SUPABASE ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- FUNCIÓN PRINCIPAL DE ARRANQUE ---
const main = () => {

    // --- MÓDULO 2: MANEJO DE PESTAÑAS ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    if (tabButtons.length > 0 && tabContents.length > 0) {
        const switchTab = (activeButton) => {
            if (!activeButton) return;
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

    // --- MÓDULO 3: MANEJO DEL CHAT DE LA IA ---
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
    
    // --- MÓDULO 4: FORMULARIO DE CAMPAÑA ---
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
        const currentBalanceElement = createCampaignTab.querySelector('#current-balance');
        const rechargeLine = createCampaignTab.querySelector('#recharge-line');
        const rechargeAmountElement = createCampaignTab.querySelector('#recharge-amount');
        const remainingLine = createCampaignTab.querySelector('#remaining-line');
        const remainingBalanceElement = createCampaignTab.querySelector('#remaining-balance');

        if (planCards.length > 0 && prospectsInput) {
            // CAMBIO PARA ADMIN: Saldo virtual alto para no bloquear el botón
            const userBalance = 1000000.00; 
            
            if(currentBalanceElement) currentBalanceElement.textContent = "∞ (Admin)";
            
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
                
                if (launchButton && summaryBox && rechargeLine && remainingLine) {
                    // Lógica de Admin: Siempre tienes saldo suficiente
                    if (userBalance >= totalCost) {
                        const remaining = userBalance - totalCost;
                        if(remainingBalanceElement) remainingBalanceElement.textContent = "Suficiente";
                        rechargeLine.style.display = 'none';
                        remainingLine.style.display = 'flex';
                        summaryBox.style.borderColor = '#28a745';
                        launchButton.disabled = false;
                    } else {
                        // Esto nunca debería pasar en modo Admin con saldo millonario
                        const needed = totalCost - userBalance;
                        if(rechargeAmountElement) rechargeAmountElement.textContent = `$${needed.toFixed(2)}`;
                        rechargeLine.style.display = 'flex';
                        remainingLine.style.display = 'none';
                        summaryBox.style.borderColor = '#ffc107';
                        launchButton.disabled = true;
                    }
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
            const defaultPlanCard = createCampaignTab.querySelector('.plan-card[data-plan="arrancador"]');
            if (defaultPlanCard) { defaultPlanCard.click(); }
            if (phoneInput) {
                window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
            }

            // --- LÓGICA DE ENVÍO DE LA CAMPAÑA (NUEVO) ---
            launchButton.addEventListener('click', async (e) => {
                e.preventDefault();
                
                // 1. Recolectar Datos
                const nombre = document.getElementById('nombre_campana').value;
                const queVende = document.getElementById('que_vendes').value;
                const aQuien = document.getElementById('a_quien_va_dirigido').value;
                const idiomas = document.getElementById('idiomas_busqueda').value;
                const ubicacion = document.getElementById('ubicacion_geografica').value;
                const descripcion = document.getElementById('descripcion_producto').value;
                const prospectosDia = prospectsInput.value;
                
                let tipoProducto = 'Tangible';
                const intangibleCheck = document.getElementById('tipo_producto_intangible');
                if (intangibleCheck && intangibleCheck.checked) {
                    tipoProducto = 'Intangible';
                }

                // 2. Validación Básica
                if (!nombre || !queVende || !ubicacion) {
                    alert("Por favor, completa los campos obligatorios: Nombre, Qué Vendes y Ubicación.");
                    return;
                }

                // 3. Efecto de Carga
                const originalText = launchButton.innerText;
                launchButton.innerText = "🚀 Iniciando Orquestador...";
                launchButton.disabled = true;

                // 4. Enviar al Backend (main.py)
                try {
                    const response = await fetch('/api/crear-campana', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            nombre: nombre,
                            que_vende: queVende,
                            descripcion: descripcion, // Descripción larga para el Analista
                            a_quien: aQuien,
                            idiomas: idiomas,
                            ubicacion: ubicacion,
                            tipo_producto: tipoProducto,
                            prospectos_dia: prospectosDia
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        alert("¡Campaña Creada Exitosamente!\n\nEl Orquestador ha recibido la orden y los Cazadores saldrán en breve.");
                        window.location.reload(); // Recargar para ver cambios si los hubiera
                    } else {
                        alert("Error al crear campaña: " + (data.error || "Desconocido"));
                        launchButton.innerText = originalText;
                        launchButton.disabled = false;
                    }

                } catch (error) {
                    console.error("Error de conexión:", error);
                    alert("Error de conexión con el servidor.");
                    launchButton.innerText = originalText;
                    launchButton.disabled = false;
                }
            });
        }
    }
    
    // --- MÓDULO 5: LOGOUT ---
    const logoutButton = document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            await supabase.auth.signOut();
            window.location.href = '/login';
        });
    }

    // --- MÓDULO 6: PESTAÑA "CONVERSACIONES" ---
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
};

// Se ejecuta el código del dashboard directamente.
main();
