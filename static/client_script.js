// --- CONFIGURACIÓN DE SUPABASE ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- FUNCIÓN PRINCIPAL DE ARRANQUE ---
const main = () => {

    // --- MÓDULO 1: MANEJO DE PESTAÑAS (INCLUYENDO LA GEMELA) ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabButtons.length > 0 && tabContents.length > 0) {
        const switchTab = (activeButton) => {
            if (!activeButton) return;
            const tabId = activeButton.getAttribute('data-tab');
            
            // Ocultar todas
            tabContents.forEach(content => content.style.display = 'none');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // Mostrar la seleccionada
            const activeTabContent = document.getElementById(tabId);
            if (activeTabContent) activeTabContent.style.display = 'block';
            activeButton.classList.add('active');

            // Si cambiamos a otra pestaña que no sea "Gestionar", ocultamos el botón gemelo
            if (tabId !== 'manage-campaign') {
                const manageBtn = document.getElementById('btn-manage-campaign');
                if (manageBtn) manageBtn.style.display = 'none'; // Se vuelve a ocultar
            }
        };

        tabButtons.forEach(button => {
            button.addEventListener('click', () => switchTab(button));
        });
        
        // Iniciar en la primera activa
        const initialActiveButton = document.querySelector('.tab-button.active');
        if (initialActiveButton) switchTab(initialActiveButton);
    }

    // --- MÓDULO 2: CARGAR DATOS DEL DASHBOARD (API REAL) ---
    const cargarDatosDashboard = async () => {
        try {
            const response = await fetch('/api/dashboard-data');
            const data = await response.json();

            // 1. Llenar KPIs
            if (data.kpis) {
                document.getElementById('kpi-total').textContent = data.kpis.total;
                document.getElementById('kpi-leads').textContent = data.kpis.calificados;
                document.getElementById('kpi-rate').textContent = data.kpis.tasa;
            }

            // 2. Llenar Tabla de Campañas
            const tbody = document.getElementById('campaigns-table-body');
            if (tbody && data.campanas) {
                tbody.innerHTML = ''; // Limpiar tabla
                data.campanas.forEach(camp => {
                    const tr = document.createElement('tr');
                    // Al hacer clic, abrimos la PESTAÑA GEMELA DE GESTIÓN
                    tr.onclick = () => abrirGestionCampana(camp);
                    tr.innerHTML = `
                        <td><strong>${camp.nombre}</strong></td>
                        <td>${camp.fecha}</td>
                        <td>${camp.estado === 'active' ? '🟢 Activa' : '🔴 Inactiva'}</td>
                        <td>${camp.encontrados}</td>
                        <td>${camp.calificados}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        } catch (error) {
            console.error("Error cargando dashboard:", error);
        }
    };

    // Llamamos a la carga inicial
    if (document.getElementById('my-campaigns')) {
        cargarDatosDashboard();
    }

    // --- MÓDULO 3: LÓGICA DE LA PESTAÑA GEMELA (GESTIÓN) ---
// --- MÓDULO 3: LÓGICA DE LA PESTAÑA GEMELA (GESTIÓN) ---
    window.abrirGestionCampana = async (campanaResumen) => {
        // 1. Mostrar pestaña y poner estado de carga
        const manageBtn = document.getElementById('btn-manage-campaign');
        manageBtn.textContent = '⚙️ Gestionar Campaña'; // Nombre corregido
        manageBtn.style.display = 'inline-block';
        manageBtn.click();
        
        document.getElementById('manage-campaign-title').textContent = 'Cargando datos...';

        try {
            // 2. Pedir expediente completo a la API
            const response = await fetch(`/api/campana/${campanaResumen.id}`); // Asumiendo que el resumen trae el ID
            
            // Si el resumen no traía ID (caso borde), necesitamos corregir el Módulo 2 para que lo traiga
            // Pero asumiendo que sí:
            
            const data = await response.json();

            if (data.error) {
                alert('Error cargando campaña');
                return;
            }

            // 3. LLENAR TODOS LOS CAMPOS (AUTO-POBLADO)
            document.getElementById('manage-campaign-title').textContent = data.nombre;
            document.getElementById('edit_campaign_id').value = data.id;
            
            // Cerebro
            document.getElementById('edit_ai_constitution').value = data.adn || '';
            document.getElementById('edit_ai_blackboard').value = data.pizarron || '';
            
            // Estrategia
            document.getElementById('edit_ubicacion').value = data.ubicacion || '';
            document.getElementById('edit_ticket').value = data.ticket || '';
            document.getElementById('edit_competidores').value = data.competidores || '';
            document.getElementById('edit_dolores').value = data.dolores || '';
            document.getElementById('edit_red_flags').value = data.red_flags || '';
            
            // Selects (asegurar que se seleccione la opción correcta)
            if(data.cta) document.getElementById('edit_cta').value = data.cta;
            if(data.tono) document.getElementById('edit_tono').value = data.tono;

        } catch (error) {
            console.error(error);
            document.getElementById('manage-campaign-title').textContent = 'Error de Conexión';
        }
    };

    // --- ACCIÓN DEL BOTÓN GUARDAR (EN PESTAÑA GESTIÓN) ---
    const btnUpdate = document.getElementById('btn-update-brain');
    if (btnUpdate) {
        btnUpdate.addEventListener('click', async () => {
            btnUpdate.textContent = 'Guardando...';
            btnUpdate.disabled = true;

            const payload = {
                id: document.getElementById('edit_campaign_id').value,
                adn: document.getElementById('edit_ai_constitution').value,
                pizarron: document.getElementById('edit_ai_blackboard').value,
                ticket: document.getElementById('edit_ticket').value,
                competidores: document.getElementById('edit_competidores').value,
                cta: document.getElementById('edit_cta').value,
                dolores: document.getElementById('edit_dolores').value,
                red_flags: document.getElementById('edit_red_flags').value,
                tono: document.getElementById('edit_tono').value
            };

            try {
                const res = await fetch('/api/actualizar-campana', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                
                if (result.success) {
                    alert('✅ Cerebro Actualizado Exitosamente');
                    btnUpdate.textContent = '💾 Guardar Cambios y Actualizar Cerebro';
                } else {
                    alert('Error guardando');
                }
            } catch (e) {
                alert('Error de conexión');
            } finally {
                btnUpdate.disabled = false;
            }
        });
    }
    // --- MÓDULO 4: MANEJO DEL CHAT DE LA IA (CONTADOR) ---
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        const userInput = document.getElementById('user-input');
        const chatMessages = document.getElementById('chat-messages');
        
        const appendMessage = (message, type) => {
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
                const data = await response.json();
                appendMessage(data.response, 'assistant');
            } catch (error) {
                appendMessage('Error de conexión con el cerebro central.', 'assistant');
            }
        });
    }
    
    // --- MÓDULO 5: FORMULARIO DE CREAR CAMPAÑA (LÓGICA PRECIOS) ---
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
        
        // Elementos de saldo
        const currentBalanceElement = createCampaignTab.querySelector('#current-balance');
        const rechargeLine = createCampaignTab.querySelector('#recharge-line');
        const rechargeAmountElement = createCampaignTab.querySelector('#recharge-amount');

        if (planCards.length > 0 && prospectsInput) {
            const userBalance = 0.00; // Esto debería venir del backend
            if(currentBalanceElement) currentBalanceElement.textContent = `$${userBalance.toFixed(2)}`;
            
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
                
                // Actualizar tarjetas visualmente
                const currentPlan = plans[activePlanKey];
                planCards.forEach(card => card.classList.remove('selected'));
                const cardToSelect = createCampaignTab.querySelector(`.plan-card[data-plan="${activePlanKey}"]`);
                if (cardToSelect) cardToSelect.classList.add('selected');
                
                // Calcular costos
                const extraProspects = prospectsCount - currentPlan.baseProspects;
                const totalCost = currentPlan.baseCost + (Math.max(0, extraProspects) * currentPlan.extraCost);
                const planName = (prospectsCount === currentPlan.baseProspects) ? currentPlan.name : 'Personalizado';
                
                // Actualizar resumen amarillo
                if(selectedPlanElement) selectedPlanElement.textContent = planName;
                if(dailyProspectsElement) dailyProspectsElement.textContent = prospectsCount;
                if(totalCostElement) totalCostElement.textContent = `$${totalCost.toFixed(2)}`;
                
                // Verificar saldo
                if (launchButton && summaryBox) {
                    if (userBalance >= totalCost) {
                        if(rechargeLine) rechargeLine.style.display = 'none';
                        summaryBox.style.borderColor = '#28a745';
                        launchButton.disabled = false;
                        launchButton.style.backgroundColor = '#28a745';
                        launchButton.textContent = 'Lanzar Campaña al Orquestador';
                    } else {
                        const needed = totalCost - userBalance;
                        if(rechargeAmountElement) rechargeAmountElement.textContent = `$${needed.toFixed(2)}`;
                        if(rechargeLine) rechargeLine.style.display = 'flex'; // Mostrar línea roja
                        summaryBox.style.borderColor = '#dc3545';
                        launchButton.disabled = true;
                        launchButton.style.backgroundColor = '#adb5bd';
                        launchButton.textContent = 'Saldo Insuficiente';
                    }
                }
            };

            // Eventos
            planCards.forEach(card => {
                card.addEventListener('click', () => {
                    const planKey = card.getAttribute('data-plan');
                    prospectsInput.value = plans[planKey].baseProspects;
                    handleFormUpdate();
                });
            });
            
            prospectsInput.addEventListener('input', handleFormUpdate);
            
            // Iniciar
            const defaultPlanCard = createCampaignTab.querySelector('.plan-card[data-plan="arrancador"]');
            if (defaultPlanCard) defaultPlanCard.click();
            
            if (phoneInput) {
                window.intlTelInput(phoneInput, { utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js" });
            }

            // --- LANZAMIENTO DE CAMPAÑA (FETCH) ---
            if (launchButton) {
                launchButton.addEventListener('click', async () => {
                    if (launchButton.disabled) return;
                    
                    launchButton.textContent = 'Enviando al Orquestador...';
                    
                    // Recopilar datos del formulario nuevo
                    const payload = {
                        nombre: document.getElementById('nombre_campana').value,
                        que_vende: document.getElementById('que_vendes').value,
                        a_quien: document.getElementById('a_quien_va_dirigido').value,
                        idiomas: document.getElementById('idiomas_busqueda').value,
                        ubicacion: document.getElementById('ubicacion_geografica').value,
                        // Datos Estratégicos Nuevos
                        ticket_producto: document.getElementById('ticket_producto').value,
                        competidores_principales: document.getElementById('competidores_principales').value,
                        objetivo_cta: document.getElementById('objetivo_cta').value,
                        dolores_pain_points: document.getElementById('dolores_pain_points').value,
                        red_flags: document.getElementById('red_flags').value,
                        tono_marca: document.getElementById('tono_marca').value,
                        // Cerebro IA
                        ai_constitution: document.getElementById('ai_constitution').value,
                        ai_blackboard: document.getElementById('ai_blackboard').value,
                        // Contacto
                        tipo_producto: document.querySelector('input[name="tipo_producto"]:checked')?.value || 'tangible',
                        whatsapp: document.getElementById('numero_whatsapp').value,
                        enlace: document.getElementById('enlace_venta').value
                    };

                    try {
                        const res = await fetch('/api/crear-campana', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(payload)
                        });
                        const data = await res.json();
                        
                        if (data.success) {
                            alert('¡Campaña Lanzada! El Orquestador ha recibido las órdenes.');
                            location.reload(); // Recargar para verla en la lista
                        } else {
                            alert('Error: ' + (data.error || 'Desconocido'));
                            launchButton.textContent = 'Intentar de nuevo';
                        }
                    } catch (e) {
                        alert('Error de conexión');
                        launchButton.textContent = 'Intentar de nuevo';
                    }
                });
            }
        }
    }
    
    // --- MÓDULO 6: LOGOUT ---
    const logoutButton = document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            await supabase.auth.signOut();
            window.location.href = '/login';
        });
    }
};

// Arrancar script
main();
