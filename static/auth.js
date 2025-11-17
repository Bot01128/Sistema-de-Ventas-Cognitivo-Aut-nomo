// --- CONFIGURACIÓN DE SUPABASE ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- LÓGICA DE LA PÁGINA DE LOGIN ---
const googleLoginButton = document.getElementById('google-login-btn');
if (googleLoginButton) {
    googleLoginButton.addEventListener('click', async () => {
        await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                // Ahora redirigimos a nuestra nueva página /callback
                redirectTo: window.location.origin + '/callback'
            }
        });
    });
}

// --- LÓGICA DEL BOTÓN DE LOGOUT ---
const logoutButton = document.getElementById('logout-btn');
if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
        await supabase.auth.signOut();
        // Al cerrar sesión, redirigimos a la página de login
        window.location.href = '/login';
    });
}

// --- MANEJO DE SESIÓN EN CADA CARGA DE PÁGINA ---
(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    const isLoginPage = window.location.pathname === '/login';

    if (!session && !isLoginPage) {
        // Si NO hay sesión y NO estamos en la página de login, forzar redirección a /login
        window.location.href = '/login';
    } else if (session && isLoginPage) {
        // Si SÍ hay sesión y estamos en la página de login, redirigir al dashboard del cliente
        window.location.href = '/cliente';
    }
})();
