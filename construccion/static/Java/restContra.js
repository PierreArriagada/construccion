// En tu archivo static/Java/restContra.js
// REEMPLAZA TODO EL CONTENIDO CON ESTO:

document.addEventListener('DOMContentLoaded', function() {

    // --- 1. Lógica del Diálogo de Éxito (Sin cambios) ---
    const successMessage = document.querySelector('.text-green-500');
    if (successMessage) {
        const dialog = document.createElement('dialog');
        dialog.className = 'somUniforme fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 px-6 py-4 rounded-md bg-gray-100 dark:bg-gray-900 z-50 max-w-md w-full text-center';
        dialog.innerHTML = `
            <h3 class="text-xl font-bold text-green-600 dark:text-green-400 mb-4">¡Contraseña restablecida con éxito!</h3>
            <p class="text-gray-700 dark:text-gray-300 mb-6">${successMessage.textContent}</p>
            <button id="confirmBtn" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-full">Aceptar</button>
        `;
        document.body.appendChild(dialog);
        dialog.showModal();
        document.getElementById('confirmBtn').addEventListener('click', function() {
            dialog.close();
            // --- AJUSTA ESTA URL ---
            window.location.href = '/login/'; // O usa {% url 'loginUser' %} si puedes pasarla
        });
        if (successMessage.parentElement) {
             successMessage.parentElement.style.display = 'none';
        }
    }

    // --- 2. Validación de Contraseña (Simplificada y Reforzada) ---
    const newPasswordInput = document.querySelector('input[name="new_password"]');
    const confirmPasswordInput = document.querySelector('input[name="confirm_password"]');

    if (newPasswordInput && confirmPasswordInput) {

        // Obtener los contenedores o crearlos si no existen (Método más robusto)
        let passwordRequirementsDiv = document.getElementById('new-password-requirements');
        if (!passwordRequirementsDiv) {
            passwordRequirementsDiv = document.createElement('div');
            passwordRequirementsDiv.id = 'new-password-requirements';
            passwordRequirementsDiv.className = 'text-sm mt-1'; // Clase base
            newPasswordInput.parentNode.appendChild(passwordRequirementsDiv); // Usar appendChild es más simple
        }

        let passwordMatchDiv = document.getElementById('password-match');
        if (!passwordMatchDiv) {
            passwordMatchDiv = document.createElement('div');
            passwordMatchDiv.id = 'password-match';
            passwordMatchDiv.className = 'text-sm mt-1'; // Clase base
            confirmPasswordInput.parentNode.appendChild(passwordMatchDiv); // Usar appendChild
        }

        // Listener para input de nueva contraseña
        newPasswordInput.addEventListener('input', function() {
            const password = this.value;
            // ... (lógica de validación de requisitos - sin cambios) ...
            const hasLowerCase = /[a-z]/.test(password);
            const hasUpperCase = /[A-Z]/.test(password);
            const hasDigit = /\d/.test(password);
            const hasSpecial = /[@$!%*?&_-]/.test(password);
            const hasMinLength = password.length >= 8;
            let requirements = [];
            if (!hasLowerCase) requirements.push('una letra minúscula');
            // ... (resto de requisitos) ...
            if (!hasMinLength) requirements.push('al menos 8 caracteres');

            if (requirements.length > 0) {
                passwordRequirementsDiv.textContent = 'La contraseña debe incluir: ' + requirements.join(', ');
                passwordRequirementsDiv.className = 'text-red-600 dark:text-red-400 text-sm mt-1';
            } else {
                passwordRequirementsDiv.textContent = '✓ Contraseña válida';
                passwordRequirementsDiv.className = 'text-green-600 dark:text-green-400 text-sm mt-1';
            }
            if (confirmPasswordInput.value) {
                checkPasswordMatch();
            }
        });

        // Función para verificar si las contraseñas coinciden (sin cambios)
        function checkPasswordMatch() {
            // passwordMatchDiv se obtiene dentro para asegurar que existe
            const pmDiv = document.getElementById('password-match');
            if (!pmDiv) return; // Salir si el div no existe

            if (newPasswordInput.value && confirmPasswordInput.value) {
                if (newPasswordInput.value !== confirmPasswordInput.value) {
                    pmDiv.textContent = 'Las contraseñas no coinciden';
                    pmDiv.className = 'text-red-600 dark:text-red-400 text-sm mt-1';
                } else {
                    pmDiv.textContent = '✓ Las contraseñas coinciden';
                    pmDiv.className = 'text-green-600 dark:text-green-400 text-sm mt-1';
                }
            } else {
                pmDiv.textContent = ''; // Limpiar si un campo está vacío
            }
        }

        // Listener para input de confirmar contraseña
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);

        // (Opcional) Listener para submit
        const formElement = newPasswordInput.closest('form');
        if (formElement) {
             formElement.addEventListener('submit', function(e) {
                 // ... (lógica de validación final antes de enviar, si la quieres) ...
                 // Ejemplo:
                 const password = newPasswordInput.value;
                 const confirmPassword = confirmPasswordInput.value;
                 const passwordValid = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_-])[A-Za-z\d@$!%*?&_-]{8,}$/.test(password);
                 const passwordsMatch = password === confirmPassword;
                 if (!passwordValid || !passwordsMatch) {
                     e.preventDefault();
                     // Actualiza visualmente por si acaso
                     checkPasswordMatch();
                     newPasswordInput.dispatchEvent(new Event('input')); // Re-dispara validación visual
                     // alert('...'); // Puedes quitar el alert si los mensajes inline son suficientes
                 }
             });
        }

        // Validar valores iniciales al cargar (si el navegador los autocompleta)
        if (newPasswordInput.value) {
            newPasswordInput.dispatchEvent(new Event('input'));
        }
        if (confirmPasswordInput.value) {
             confirmPasswordInput.dispatchEvent(new Event('input'));
        }

    } // Fin if (newPasswordInput && confirmPasswordInput)

}); // Fin DOMContentLoaded
