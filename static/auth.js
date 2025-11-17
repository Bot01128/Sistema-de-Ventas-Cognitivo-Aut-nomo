// --- CONFIGURACIÓN DE SUPABASE (NECESITAREMOS ESTAS LLAVES) ---
const SUPABASE_URL = 'https://fxduwnictssgxqndokly.supabase.co'; 
// Esta es tu URL pública de Supabase.
const SUPABASE_ANON_KEY = 'TU_SUPABASE_ANON_KEY'; 
// ¡IMPORTANTE! Reemplaza esto con tu clave "anon" de Supabase.

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// --- LÓGICA DEL BOTÓN DE LOGIN ---
const googleLoginButton = document.getElementById('google-login-btn');

if (googleLoginButton) {
    googleLoginButton.addEventListener('click', async () => {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
        });

        if (error) {
            console.error('Error al iniciar sesión con Google:', error.message);
            alert('Hubo un error al intentar iniciar sesión. Por favor, intenta de nuevo.');
        }
    });
}
```**Acción Requerida:** Para que este código funcione, necesitas reemplazar `'TU_SUPABASE_ANON_KEY'` por tu clave real. Aquí te digo cómo encontrarla:
*   Ve a tu proyecto en **Supabase**.
*   Haz clic en el icono de **engranaje (Settings)**.
*   En el menú, haz clic en **`API`**.
*   En la sección "Project API keys", verás una clave llamada `anon` `public`. **Copia esa clave** y pégala en el archivo `auth.js`.

---

### **3. El Python: `main.py`**

**Instrucción:** Abre tu archivo `main.py` y añade esta nueva ruta `/login`. Puedes ponerla junto a las otras rutas de la aplicación.

```python
# AÑADE ESTA NUEVA RUTA EN main.py

@app.route('/login')
def login():
    return render_template('login.html')
