// --- CONFIGURACIÓN DE SUPABASE ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- FUNCIÓN PRINCIPAL DE ARRANQUE ---
const mainAuth = async () => {
    // Primero, intentamos obtener la sesión del usuario actual
    const { data: { session } } = await supabase.auth.getSession();
    
    // Verificamos en qué página estamos
    const isLoginPage = window.location.pathname.endsWith('/login');
    const isCallbackPage = window.location.pathname.endsWith('/callback');

    // Si estamos en la página de callback, no hacemos nada, dejamos que su propio script actúe.
    if (isCallbackPage) {
        return;
    }

    // --- LÓGICA DE ENRUTAMIENTO ---
    if (!session && !isLoginPage) {
        // CASO 1: No hay sesión y NO estamos en la página de login.
        // ACCIÓN: Forzar redirección a la página de login.
        window.location.href = '/login';
    } else if (session && isLoginPage) {
        // CASO 2: Sí hay sesión y estamos intentando acceder a la página de login.
        // ACCIÓN: Ya está logueado, lo redirigimos a su dashboard.
        window.location.href = '/cliente';
    }

    // --- LÓGICA DE LOS BOTONES (Solo se activa si los botones existen) ---
    const googleLoginButton = document.getElementById('google-login-btn');
    if (googleLoginButton) {
        googleLoginButton.addEventListener('click', async () => {
            await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: window.location.origin + '/callback'
                }
            });
        });
    }

    const logoutButton = document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', async () => {
            await supabase.auth.signOut();
            window.location.href = '/login';
        });
    }
};

// Ejecutamos la función principal al cargar el script
mainAuth();
