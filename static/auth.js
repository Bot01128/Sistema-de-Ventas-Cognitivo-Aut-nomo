// --- CONFIGURACIÓN DE SUPABASE (CON LA CLAVE REAL) ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- LÓGICA DE LA PÁGINA DE LOGIN ---
const googleLoginButton = document.getElementById('google-login-btn');
if (googleLoginButton) {
    googleLoginButton.addEventListener('click', async () => {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                // === CAMBIO IMPORTANTE: Redirige a la ruta raíz para que el servidor decida ===
                redirectTo: window.location.origin 
            }
        });
        if (error) {
            console.error('Error al iniciar sesión con Google:', error.message);
            alert('Hubo un error al intentar iniciar sesión. Por favor, intenta de nuevo.');
        }
    });
}

// --- LÓGICA DEL BOTÓN DE LOGOUT ---
const logoutButton = document.getElementById('logout-btn');
if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
        const { error } = await supabase.auth.signOut();
        if (!error) {
            window.location.href = '/login';
        } else {
            console.error('Error al cerrar sesión:', error.message);
        }
    });
}

// --- PROTECCIÓN DE RUTAS ---
// (Por ahora, mantenemos esta lógica simple. La mejoraremos en la siguiente fase)
supabase.auth.onAuthStateChange((event, session) => {
    if (!session && window.location.pathname !== '/login') {
        // Si no hay sesión y no estamos ya en la página de login, lo mandamos para allá.
        // window.location.href = '/login'; // Desactivado temporalmente para no causar bucles
    }
});
