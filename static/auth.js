// --- CONFIGURACIÓN DE SUPABASE ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- LÓGICA DE LA PÁGINA DE LOGIN ---
// Solo se ejecuta si encontramos el botón de login
const googleLoginButton = document.getElementById('google-login-btn');
if (googleLoginButton) {
    googleLoginButton.addEventListener('click', async () => {
        await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                // Después de que Google autorice, lo enviamos a /callback
                redirectTo: window.location.origin + '/callback'
            }
        });
    });
}

// --- LÓGICA DEL BOTÓN DE LOGOUT ---
// Solo se ejecuta si encontramos el botón de logout
const logoutButton = document.getElementById('logout-btn');
if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
        await supabase.auth.signOut();
        // Después de cerrar sesión, siempre lo enviamos a /login
        window.location.href = '/login';
    });
}

// --- EL GUARDIA DE SEGURIDAD (LA PARTE MÁS IMPORTANTE) ---
// Esta función se ejecuta en TODAS las páginas que incluyan este script.
const protectPage = async () => {
    // Verificamos si estamos en una página pública que no necesita protección
    const isPublicPage = window.location.pathname === '/login' || window.location.pathname === '/callback';
    
    // Si estamos en una página pública, no hacemos nada más.
    if (isPublicPage) {
        return;
    }

    // Si estamos en cualquier OTRA página, verificamos la sesión
    const { data: { session } } = await supabase.auth.getSession();

    if (!session) {
        // Si NO hay sesión, es un intruso. Lo enviamos a la página de login.
        window.location.href = '/login';
    }
    // Si hay sesión, no hacemos nada y dejamos que el usuario vea la página.
};

// Ejecutamos al guardia de seguridad en cuanto se carga la página.
protectPage();
