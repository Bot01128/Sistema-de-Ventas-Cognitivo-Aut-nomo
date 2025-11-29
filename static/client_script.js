// --- CONFIGURACIÓN DE SUPABASE ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const main = () => {
    // --- 1. PESTAÑAS ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    const switchTab = (activeButton) => {
        const tabId = activeButton.getAttribute('data-tab');
        tabContents.forEach(c => c.style.display = 'none');
        tabButtons.forEach(b => b.classList.remove('active'));
        document.getElementById(tabId).style.display = 'block';
        activeButton.classList.add('active');
        if (tabId !== 'manage-campaign') {
            document.getElementById('btn-manage-campaign').style.display = 'none';
        }
    };
    tabButtons.forEach(btn => btn.addEventListener('click', () => switchTab(btn)));

    // --- 2. ABRIR GESTIÓN (LLENADO COMPLETO) ---
    window.abrirGestionCampana = async (campanaResumen) => {
        const manageBtn = document.getElementById('btn-manage-campaign');
        manageBtn.style.display = 'inline-block';
        manageBtn.click();
        document.getElementById('manage-campaign-title').textContent = 'Cargando...';

        try {
            const res = await fetch(`/api/campana/${campanaResumen.id}`);
            const data = await res.json();

            if(data.error) { alert('Error cargando datos'); return; }

            // Llenar Cabecera
            document.getElementById('manage-campaign-title').textContent = data.nombre;
            document.getElementById('edit_campaign_id').value = data.id;

            // A. Plan Visual (Resaltar el actual)
            const limit = data.limite_diario || 4;
            document.querySelectorAll('#manage-campaign .plan-card').forEach(c => c.classList.remove('selected'));
            if (limit <= 14) document.getElementById('edit_plan_arrancador').classList.add('selected');
            else if (limit <= 49) document.getElementById('edit_plan_profesional').classList.add('selected');
            else document.getElementById('edit_plan_dominador').classList.add('selected');

            // B. Datos Básicos
            document.getElementById('edit_nombre_campana').value = data.nombre || '';
            // Separamos "Que vendes" de la descripción (un truco simple)
            const descParts = (data.descripcion || '').split('. ');
            document.getElementById('edit_que_vendes').value = descParts[0] || '';
            
            document.getElementById('edit_a_quien_va_dirigido').value = data.audiencia || '';
            document.getElementById('edit_idiomas_busqueda').value = data.idiomas || '';
            document.getElementById('edit_ubicacion_geografica').value = data.ubicacion || '';

            // C. Estrategia
            document.getElementById('edit_ticket_producto').value = data.ticket || '';
            document.getElementById('edit_competidores_principales').value = data.competidores || '';
            document.getElementById('edit_dolores_pain_points').value = data.dolores || '';
            document.getElementById('edit_red_flags').value = data.red_flags || '';
            if(data.cta) document.getElementById('edit_objetivo_cta').value = data.cta;
            if(data.tono) document.getElementById('edit_tono_marca').value = data.tono;

            // D. Cerebro
            document.getElementById('edit_ai_constitution').value = data.adn || '';
            document.getElementById('edit_ai_blackboard').value = data.pizarron || '';

            // E. Contacto (Necesitamos actualizar main.py para enviar esto, ver paso 3)
            // Por ahora dejamos los campos listos

        } catch (e) { console.error(e); }
    };

    // --- 3. GUARDAR CAMBIOS ---
    const btnUpdate = document.getElementById('btn-update-brain');
    if(btnUpdate) {
        btnUpdate.addEventListener('click', async () => {
            btnUpdate.textContent = 'Guardando...';
            btnUpdate.disabled = true;
            
            // Reconstruimos la descripción
            const descFull = `${document.getElementById('edit_que_vendes').value}.`;

            const payload = {
                id: document.getElementById('edit_campaign_id').value,
                nombre: document.getElementById('edit_nombre_campana').value,
                descripcion: descFull,
                audiencia: document.getElementById('edit_a_quien_va_dirigido').value,
                idiomas: document.getElementById('edit_idiomas_busqueda').value,
                ticket: document.getElementById('edit_ticket_producto').value,
                competidores: document.getElementById('edit_competidores_principales').value,
                cta: document.getElementById('edit_objetivo_cta').value,
                dolores: document.getElementById('edit_dolores_pain_points').value,
                red_flags: document.getElementById('edit_red_flags').value,
                tono: document.getElementById('edit_tono_marca').value,
                adn: document.getElementById('edit_ai_constitution').value,
                pizarron: document.getElementById('edit_ai_blackboard').value
            };

            try {
                const res = await fetch('/api/actualizar-campana', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const r = await res.json();
                if (r.success) alert('✅ Campaña Actualizada'); else alert('Error');
            } catch (e) { alert('Error conexión'); }
            finally { btnUpdate.disabled = false; btnUpdate.textContent = '💾 Guardar Todos los Cambios'; }
        });
    }

    // --- CARGAR DASHBOARD ---
    const cargarDashboard = async () => {
        try {
            const res = await fetch('/api/dashboard-data');
            const data = await res.json();
            const tbody = document.getElementById('campaigns-table-body');
            tbody.innerHTML = '';
            data.campanas.forEach(c => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td><strong>${c.nombre}</strong></td><td>${c.fecha}</td><td>${c.estado}</td><td>${c.encontrados}</td><td>${c.calificados}</td>`;
                tr.onclick = () => abrirGestionCampana(c);
                tbody.appendChild(tr);
            });
            document.getElementById('kpi-total').textContent = data.kpis.total;
        } catch(e) {}
    };
    if(document.getElementById('my-campaigns')) cargarDashboard();

    // --- FORMULARIO CREAR (LÓGICA PRECIOS) ---
    const createTab = document.getElementById('create-campaign');
    if (createTab) {
        const plans = {
            arrancador: { base: 4, cost: 149, extra: 37.25, limit: 14 },
            profesional: { base: 15, cost: 399, extra: 26.60, limit: 49 },
            dominador: { base: 50, cost: 999, extra: 20.00, limit: 9999 }
        };
        const input = document.getElementById('prospects-per-day');
        const totalElem = document.getElementById('total-cost');
        const planNameElem = document.getElementById('selected-plan');
        const rechargeElem = document.getElementById('recharge-amount');
        const btnLanzar = document.getElementById('lancam');
        const summaryBox = document.getElementById('summary-box');

        const updateCalc = () => {
            const val = parseInt(input.value) || 4;
            let key = 'dominador';
            if (val <= 14) key = 'arrancador';
            else if (val <= 49) key = 'profesional';
            
            const p = plans[key];
            const extra = Math.max(0, val - p.base);
            const cost = p.cost + (extra * p.extra);
            const userBal = 0.00; 

            planNameElem.textContent = key.charAt(0).toUpperCase() + key.slice(1);
            totalElem.textContent = `$${cost.toFixed(2)}`;
            
            if (userBal >= cost) {
                summaryBox.style.backgroundColor = '#d4edda';
                summaryBox.style.borderColor = '#c3e6cb';
                rechargeElem.parentElement.style.display = 'none';
                btnLanzar.disabled = false;
                btnLanzar.textContent = 'Lanzar Campaña al Orquestador';
            } else {
                summaryBox.style.backgroundColor = '#fff3cd';
                summaryBox.style.borderColor = '#ffeeba';
                rechargeElem.textContent = `$${(cost - userBal).toFixed(2)}`;
                rechargeElem.parentElement.style.display = 'flex';
                btnLanzar.disabled = true;
                btnLanzar.textContent = 'Saldo Insuficiente';
            }
            document.querySelectorAll('#create-campaign .plan-card').forEach(c => c.classList.remove('selected'));
            document.querySelector(`#create-campaign .plan-card[data-plan="${key}"]`).classList.add('selected');
        };

        input.addEventListener('input', updateCalc);
        document.querySelectorAll('#create-campaign .plan-card').forEach(c => {
            c.addEventListener('click', () => {
                input.value = plans[c.dataset.plan].base;
                updateCalc();
            });
        });
        updateCalc();
        
        btnLanzar.addEventListener('click', async () => {
            const payload = {
                nombre: document.getElementById('nombre_campana').value,
                que_vende: document.getElementById('que_vendes').value,
                tipo_producto: document.querySelector('input[name="tipo_producto"]:checked').value,
                ai_constitution: document.getElementById('ai_constitution').value,
                ai_blackboard: document.getElementById('ai_blackboard').value,
                a_quien: document.getElementById('a_quien_va_dirigido').value,
                idiomas: document.getElementById('idiomas_busqueda').value,
                ubicacion: document.getElementById('ubicacion_geografica').value,
                ticket_producto: document.getElementById('ticket_producto').value,
                competidores_principales: document.getElementById('competidores_principales').value,
                objetivo_cta: document.getElementById('objetivo_cta').value,
                dolores_pain_points: document.getElementById('dolores_pain_points').value,
                red_flags: document.getElementById('red_flags').value,
                tono_marca: document.getElementById('tono_marca').value,
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
                    alert('¡Campaña Lanzada!');
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (e) { alert('Error de conexión'); }
        });
    }
};
main();
