// --- CONFIGURACIÓN DE SUPABASE ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const main = () => {

    // --- MÓDULO 2: MANEJO DE PESTAÑAS ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    if (tabButtons.length > 0) {
        const switchTab = (activeButton) => {
            const tabId = activeButton.getAttribute('data-tab');
            const activeTabContent = document.getElementById(tabId);
            tabContents.forEach(content => content.style.display = 'none');
            if (activeTabContent) activeTabContent.style.display = 'block';
            tabButtons.forEach(btn => btn.classList.remove('active'));
            activeButton.classList.add('active');
        };
        tabButtons.forEach(button => button.addEventListener('click', () => switchTab(button)));
        const initialBtn = document.querySelector('.tab-button.active');
        if (initialBtn) switchTab(initialBtn);
    }

    // --- MÓDULO 4: FORMULARIO DE CAMPAÑA (ADMIN) ---
    const createCampaignTab = document.getElementById('create-campaign');
    if (createCampaignTab) {
        const launchButton = createCampaignTab.querySelector('#lancam');
        const prospectsInput = createCampaignTab.querySelector('#prospects-per-day');
        const phoneInput = createCampaignTab.querySelector("#numero_whatsapp");
        
        // Inicializar input de teléfono bonito
        if (phoneInput) {
            window.intlTelInput(phoneInput, { 
                utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
                preferredCountries: ['co', 'mx', 'us', 'es']
            });
        }

        // Configuración visual del plan
        const planCards = createCampaignTab.querySelectorAll('.plan-card');
        if (planCards.length > 0) {
            planCards.forEach(card => {
                card.addEventListener('click', () => {
                    planCards.forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    if (card.dataset.plan === 'arrancador') prospectsInput.value = 4;
                    if (card.dataset.plan === 'profesional') prospectsInput.value = 15;
                    if (card.dataset.plan === 'dominador') prospectsInput.value = 50;
                });
            });
        }

        // --- LÓGICA DE ENVÍO DE CAMPAÑA ---
        if (launchButton) {
            launchButton.addEventListener('click', async (e) => {
                e.preventDefault();
                
                // 1. RECOLECTAR DATOS
                const nombre = document.getElementById('nombre_campana').value.trim();
                const queVende = document.getElementById('que_vendes').value.trim();
                const aQuien = document.getElementById('a_quien_va_dirigido').value.trim();
                const idiomas = document.getElementById('idiomas_busqueda').value.trim();
                const ubicacion = document.getElementById('ubicacion_geografica').value.trim();
                const descripcion = document.getElementById('descripcion_producto').value.trim();
                const enlaceVenta = document.getElementById('enlace_venta').value.trim();
                const whatsapp = phoneInput ? phoneInput.value.trim() : "";
                const prospectosDia = prospectsInput ? prospectsInput.value : 4;
                
                // 2. VALIDACIÓN DE TIPO DE PRODUCTO (OBLIGATORIO)
                const tangibleCheck = document.getElementById('tipo_producto_tangible');
                const intangibleCheck = document.getElementById('tipo_producto_intangible');
                let tipoProducto = null;

                if (tangibleCheck.checked) tipoProducto = 'Tangible';
                if (intangibleCheck.checked) tipoProducto = 'Intangible';

                // 3. VALIDACIÓN ESTRICTA (MANO DURA) 🛡️
                let faltantes = [];
                if (!nombre) faltantes.push("Nombre de la Campaña");
                if (!queVende) faltantes.push("¿Qué vendes?");
                if (!aQuien) faltantes.push("¿A quién va dirigido?");
                if (!ubicacion) faltantes.push("Ubicación Geográfica");
                if (!idiomas) faltantes.push("Idiomas");
                if (!tipoProducto) faltantes.push("Tipo de Producto (Tangible/Intangible)");
                if (!descripcion) faltantes.push("Descripción del Producto");
                if (!whatsapp) faltantes.push("Número de WhatsApp");
                if (!enlaceVenta) faltantes.push("Enlace de Venta");

                if (faltantes.length > 0) {
                    alert("⚠️ ¡ALTO AHÍ! FALTAN DATOS OBLIGATORIOS\n\nPara vender con éxito, el sistema necesita:\n\n- " + faltantes.join("\n- "));
                    return; // Detiene todo aquí
                }

                // 4. Efecto de Carga
                const originalText = launchButton.innerText;
                launchButton.innerText = "🚀 Contactando al Orquestador...";
                launchButton.disabled = true;

                // 5. Enviar al Backend
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

                    // Manejo de respuesta (Incluyendo el 404)
                    if (response.status === 404) {
                        throw new Error("Ruta no encontrada (404). El archivo main.py no tiene la función '/api/crear-campana'. Verifica GitHub.");
                    }

                    const contentType = response.headers.get("content-type");
                    if (contentType && contentType.indexOf("application/json") !== -1) {
                        const data = await response.json();
                        if (data.success) {
                            alert("✅ ¡CAMPAÑA LANZADA CON ÉXITO!\n\nEl Orquestador ha recibido la orden.\nRevisa la tabla 'Prospectos' en unos minutos.");
                            window.location.reload();
                        } else {
                            alert("❌ ERROR DEL SERVIDOR:\n" + data.error);
                        }
                    } else {
                        const text = await response.text();
                        alert("❌ ERROR CRÍTICO DE RESPUESTA:\n" + text.substring(0, 150) + "...");
                    }

                } catch (error) {
                    console.error("Error:", error);
                    alert("❌ ERROR DE CONEXIÓN:\n" + error.message);
                } finally {
                    launchButton.innerText = originalText;
                    launchButton.disabled = false;
                }
            });
        }
    }
};

main();
