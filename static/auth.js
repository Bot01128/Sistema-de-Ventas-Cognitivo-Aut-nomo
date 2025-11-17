// --- CONFIGURACIÓN DE SUPABASE ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- FUNCIÓN DE GESTIÓN DE SESIÓN Y PROTECCIÓN DE RUTAS ---
const handleAuth = async () => {
    // 1. Obtiene la sesión actual. Esta función espera a que Supabase esté listo.
    const { data: { session } } = await supabase.auth.getSession();
    
    // 2. Define en qué página estamos.
    const isLoginPage = window.location.pathname.endsWith('/login');
    const isCallbackPage = window.location.pathname.endsWith('/callback');

    // 3. Si estamos en la página de callback, detenemos la ejecución aquí.
    if (isCallbackPage) {
        return; 
    }

    // 4. Lógica de redirección, ahora sí, garantizada.
    if (!session && !isLoginPage) {
        // Si NO hay sesión y NO estamos en la página de login, es un intruso.
        // Lo enviamos a la puerta de entrada.
        window.location.href = '/login';
    } else if (session && isLoginPage) {
        // Si SÍ hay sesión y está intentando volver a la página de login,
        // lo mandamos directamente a su dashboard.
        window.location.href = '/cliente';
    }
};

// --- INICIALIZACIÓN DE LA LÓGICA EN LA PÁGINA ---

// Lógica para la página de Login
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

// Lógica para el botón de Logout
const logoutButton = document.getElementById('logout-btn');
if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
        await supabase.auth.signOut();
        window.location.href = '/login';
    });
}

// --- EJECUCIÓN DEL GUARDIA DE SEGURIDAD ---
// Ejecutamos nuestra función principal de autenticación.
handleAuth();
