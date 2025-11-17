// --- CONFIGURACIÓN DE SUPABASE (CON LA CLAVE REAL Y ACTUALIZADA) ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ4ZHV3bmljdHNzZ3hxbmRva2x5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMzc3NDgsImV4cCI6MjA3NzYxMzc0OH0.1uqbiNroOCvAsn08Ps7JZpXV9K-rUyLfukOL5w4X_eg';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- LÓGICA DEL BOTÓN DE LOGIN ---
const googleLoginButton = document.getElementById('google-login-btn');

if (googleLoginButton) {
    googleLoginButton.addEventListener('click', async () => {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                // Redirige al usuario al dashboard del cliente después de un login exitoso
                redirectTo: window.location.origin + '/cliente'
            }
        });

        if (error) {
            console.error('Error al iniciar sesión con Google:', error.message);
            alert('Hubo un error al intentar iniciar sesión. Por favor, intenta de nuevo.');
        }
    });
}
