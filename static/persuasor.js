document.addEventListener('DOMContentLoaded', function() {
    
    const nidoForm = document.getElementById('nido-form');

    if (nidoForm) {
        nidoForm.addEventListener('submit', function(event) {
            // Prevenimos el envío inmediato del formulario para mostrar un mensaje
            event.preventDefault();

            const emailInput = nidoForm.querySelector('input[type="email"]');
            
            if (emailInput && emailInput.value.trim() !== '') {
                // Mostramos un mensaje de éxito
                alert('¡Excelente! Estamos generando tu análisis personalizado. Serás redirigido en un momento...');
                
                // Después de 1 segundo, enviamos el formulario
                setTimeout(function() {
                    nidoForm.submit();
                }, 1000);

            } else {
                // Si el campo de email está vacío (aunque 'required' debería prevenir esto)
                alert('Por favor, introduce tu correo electrónico para continuar.');
            }
        });
    }
});
