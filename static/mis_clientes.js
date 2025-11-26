document.addEventListener('DOMContentLoaded', () => {

    // 1. TABS
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length > 0) {
        const switchTab = (btn) => {
            const tabId = btn.getAttribute('data-tab');
            tabContents.forEach(c => c.style.display = 'none');
            tabButtons.forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).style.display = 'block';
            btn.classList.add('active');
        };
        tabButtons.forEach(b => b.addEventListener('click', () => switchTab(b)));
        switchTab(tabButtons[0]); // Activar primera
    }

    // 2. CARGAR DATOS DEL DASHBOARD (¡ESTO FALTABA!)
    const loadDashboardData = async () => {
        try {
            const response = await fetch('/api/dashboard-data');
            if (!response.ok) return;
            const data = await response.json();

            // Actualizar KPIs
            const kpis = document.querySelectorAll('.kpi-value');
            if (kpis.length >= 3) {
                kpis[0].innerText = data.kpis.total;
                kpis[1].innerText = data.kpis.calificados;
                kpis[2].innerText = data.kpis.tasa;
            }

            // Actualizar Tabla
            const tbody = document.querySelector('.campaign-table tbody');
            if (tbody) {
                tbody.innerHTML = ''; // Limpiar tabla
                data.campanas.forEach(c => {
                    const row = `<tr>
                        <td>${c.nombre}</td>
                        <td>${c.fecha}</td>
                        <td>${c.estado === 'active' ? 'Activa 🟢' : c.estado}</td>
                        <td>${c.encontrados}</td>
                        <td>${c.calificados}</td>
                    </tr>`;
                    tbody.innerHTML += row;
                });
            }
        } catch (error) {
            console.error("Error cargando datos:", error);
        }
    };

    // Llamar a la función de carga al inicio
    loadDashboardData();
    // Recargar cada 30 segundos para ver progreso en vivo
    setInterval(loadDashboardData, 30000);

    // 3. CHATBOT
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = document.getElementById('user-input');
            const msg = input.value.trim();
            if (!msg) return;
            
            const box = document.getElementById('chat-messages');
            box.innerHTML += `<p class="msg-user">${msg}</p>`;
            input.value = '';
            box.scrollTop = box.scrollHeight;

            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await res.json();
            box.innerHTML += `<p class="msg-assistant">${data.response}</p>`;
            box.scrollTop = box.scrollHeight;
        });
    }

    // 4. CREAR CAMPAÑA
    const launchBtn = document.getElementById('lancam');
    if (launchBtn) {
        launchBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            // ... (Lógica de recolección de datos igual a la anterior) ...
            // Para ahorrar espacio, asumo que mantienes la lógica de validación
            // Si quieres el bloque completo de nuevo, pídemelo, pero lo importante arriba es loadDashboardData
            
            // Simulación rápida del envío para no borrar tu lógica existente
            const nombre = document.getElementById('nombre_campana').value;
            if(!nombre) { alert("Falta nombre"); return; }
            
            launchBtn.innerText = "Enviando...";
            const res = await fetch('/api/crear-campana', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    nombre: nombre,
                    que_vende: document.getElementById('que_vendes').value,
                    // ... resto de campos
                    descripcion: document.getElementById('descripcion_producto').value
                })
            });
            const d = await res.json();
            if(d.success) {
                alert("Campaña Creada");
                window.location.reload();
            } else {
                alert("Error");
            }
            launchBtn.innerText = "Lanzar Campaña";
        });
    }
});
