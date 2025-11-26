document.addEventListener('DOMContentLoaded', () => {

    // ============================================================================
    // 1. SISTEMA DE PESTAÑAS (TABS)
    // ============================================================================
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length > 0 && tabContents.length > 0) {
        const switchTab = (activeButton) => {
            if (!activeButton) return;
            const tabId = activeButton.getAttribute('data-tab');
            
            // Ocultar todo
            tabContents.forEach(content => content.style.display = 'none');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // Mostrar seleccionado
            const activeTabContent = document.getElementById(tabId);
            if (activeTabContent) activeTabContent.style.display = 'block';
            activeButton.classList.add('active');
        };

        tabButtons.forEach(button => {
            button.addEventListener('click', () => switchTab(button));
        });

        // Activar la primera pestaña por defecto
        const initialActiveButton = document.querySelector('.tab-button.active');
        if (initialActiveButton) {
            switchTab(initialActiveButton);
        }
    }

    // ============================================================================
    // 2. CHATBOT DEL DASHBOARD (SOPORTE AL CLIENTE)
    // ============================================================================
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

                if (!response.ok) throw new Error('Error de conexión con el cerebro');
                
                const data = await response.json();
                appendMessage(data.response, 'assistant');

            } catch (error) {
                console.error('Error chat:', error);
                appendMessage('Lo siento, estoy teniendo problemas de conexión momentáneos.', 'assistant');
            }
        });
    }

    // ============================================================================
    // 3. FORMULARIO DE CREACIÓN DE CAMPAÑA (LÓGICA DE NEGOCIO)
    // ============================================================================
    const createCampaignTab = document.getElementById('create-campaign');
    if (createCampaignTab) {
        const launchButton = document.getElementById('lancam');
        const prospectsInput = document.getElementById('prospects-per-day');
        const phoneInput = document.getElementById("numero_whatsapp");

        // Inicializar input de teléfono internacional
        if (phoneInput && window.intlTelInput) {
            window.intlTelInput(phoneInput, { 
                utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
                preferredCountries: ['es', 'mx', 'co', 'us']
            });
        }

        // Lógica del botón "Lanzar Campaña"
        if (launchButton) {
            launchButton.addEventListener('click', async (e) => {
                e.preventDefault();
                
                // Recolección de datos
                const nombre = document.getElementById('nombre_campana').value.trim();
                const queVende = document.getElementById('que_vendes').value.trim();
                const aQuien = document.getElementById('a_quien_va_dirigido').value.trim();
                const idiomas = document.getElementById('idiomas_busqueda').value.trim();
                const ubicacion = document.getElementById('ubicacion_geografica').value.trim();
                const descripcion = document.getElementById('descripcion_producto').value.trim();
                const enlaceVenta = document.getElementById('enlace_venta').value.trim();
                const whatsapp = phoneInput ? phoneInput.value.trim() : "";
                const prospectosDia = prospectsInput ? prospectsInput.value : 4;
                
                // Checkbox de tipo de producto
                const tangibleCheck = document.getElementById('tipo_producto_tangible');
                const intangibleCheck = document.getElementById('tipo_producto_intangible');
                let tipoProducto = null;

                if (tangibleCheck && tangibleCheck.checked) tipoProducto = 'Tangible';
                if (intangibleCheck && intangibleCheck.checked) tipoProducto = 'Intangible';

                // Validación
                let faltantes = [];
                if (!nombre) faltantes.push("Nombre de la Campaña");
                if (!queVende) faltantes.push("¿Qué vendes?");
                if (!aQuien) faltantes.push("¿A quién va dirigido?");
                if (!ubicacion) faltantes.push("Ubicación Geográfica");
                if (!idiomas) faltantes.push("Idiomas");
                if (!tipoProducto) faltantes.push("Tipo de Producto");
                if (!descripcion) faltantes.push("Descripción Detallada");
                if (!whatsapp) faltantes.push("WhatsApp");
                if (!enlaceVenta) faltantes.push("Enlace de Venta");

                if (faltantes.length > 0) {
                    alert("⚠️ FALTAN DATOS:\n- " + faltantes.join("\n- "));
                    return;
                }

                // Estado de carga
                const originalText = launchButton.innerText;
                launchButton.innerText = "🚀 Enviando al Orquestador...";
                launchButton.disabled = true;

                try {
                    const response = await fetch('/api/crear-campana', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            nombre: nombre,
                            que_vende: queVende,
                            descripcion: descripcion,
                            a_quien: aQuien,
                            idiomas: idiomas,
                            ubicacion: ubicacion,
                            tipo_producto: tipoProducto,
                            prospectos_dia: prospectosDia,
                            whatsapp: whatsapp,
                            enlace_venta: enlaceVenta
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        alert("✅ ¡CAMPAÑA LANZADA CON ÉXITO!\nEl Orquestador ha recibido la orden.");
                        window.location.reload();
                    } else {
                        alert("❌ Error del servidor: " + (data.error || "Desconocido"));
                    }

                } catch (error) {
                    console.error("Error:", error);
                    alert("❌ Error de conexión. Verifica tu internet.");
                } finally {
                    launchButton.innerText = originalText;
                    launchButton.disabled = false;
                }
            });
        }
    }

    // ============================================================================
    // 4. CARGA DE DATOS (TABLA DE CAMPAÑAS)
    // ============================================================================
    // Esta función se conecta a Supabase (o API propia) para llenar la tabla
    // Aquí simularemos la carga para que veas que funciona la UI
    // En producción, esto debería hacer un fetch a /api/get-campaigns
    
    /*
    const loadCampaigns = async () => {
        try {
            // Aquí iría el fetch real
            // const res = await fetch('/api/mis-campanas');
            // const campaigns = await res.json();
            // renderCampaignTable(campaigns);
        } catch (e) {
            console.error("Error cargando campañas:", e);
        }
    };
    // loadCampaigns(); 
    */

});
