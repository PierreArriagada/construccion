$(document).ready(function() {
    // Primero, añadir elementos para mostrar errores de validación en tiempo real
    // que no interfieran con los errores de Django
    $('form input, form select, form textarea').each(function() {
        const fieldId = $(this).attr('id');
        if (fieldId) {
            const errorId = fieldId + '-js-error';
            if ($('#' + errorId).length === 0) {
                $(this).after('<p id="' + errorId + '" class="text-red-500 text-xs italic mt-1 hidden"></p>');
            }
        }
    });

    // Nombre Completo
    $("#id_nombre_completo").on("input", function() {
        if ($(this).val().trim() === "") {
            $("#id_nombre_completo-js-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else {
            $("#id_nombre_completo-js-error").addClass("hidden");
        }
    });

    // Nombre de Usuario
    $("#id_nombre_usuario").on("input", function() {
        if ($(this).val().trim() === "") {
            $("#id_nombre_usuario-js-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else {
            $("#id_nombre_usuario-js-error").addClass("hidden");
        }
    });

    // Correo Electrónico
    $("#id_correo_electronico").on("input", function() {
        let emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if ($(this).val().trim() === "") {
            $("#id_correo_electronico-js-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else if (!emailRegex.test($(this).val().trim())) {
            $("#id_correo_electronico-js-error").text("Por favor, ingresa un correo electrónico válido.").removeClass("hidden");
        } else {
            $("#id_correo_electronico-js-error").addClass("hidden");
        }
    });

    // Contraseña
    $("#id_contrasena").on("input", function() {
        let passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]).{8,}$/;
        if ($(this).val().trim() === "") {
            $("#id_contrasena-js-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else if (!passwordRegex.test($(this).val())) {
            $("#id_contrasena-js-error").text("La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una letra minúscula, un número y un carácter especial.").removeClass("hidden");
        } else {
            $("#id_contrasena-js-error").addClass("hidden");
        }
        
        // Validar repetir contraseña cuando cambia la contraseña original
        if ($("#id_repetir_contrasena").val() !== "") {
            if ($("#id_repetir_contrasena").val() !== $(this).val()) {
                $("#id_repetir_contrasena-js-error").text("Las contraseñas no coinciden.").removeClass("hidden");
            } else {
                $("#id_repetir_contrasena-js-error").addClass("hidden");
            }
        }
    });

    // Repetir Contraseña
    $("#id_repetir_contrasena").on("input", function() {
        if ($(this).val().trim() === "") {
            $("#id_repetir_contrasena-js-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else if ($(this).val() !== $("#id_contrasena").val()) {
            $("#id_repetir_contrasena-js-error").text("Las contraseñas no coinciden.").removeClass("hidden");
        } else {
            $("#id_repetir_contrasena-js-error").addClass("hidden");
        }
    });

    // Número de Teléfono
    $("#id_numero_telefono").on("input", function() {
        let telefonoRegex = /^\d{1,9}$/;
        if ($(this).val().trim() === "") {
            $("#id_numero_telefono-js-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else if (!telefonoRegex.test($(this).val().trim())) {
            $("#id_numero_telefono-js-error").text("El número de teléfono debe contener solo números y tener como máximo 9 dígitos.").removeClass("hidden");
        } else {
            $("#id_numero_telefono-js-error").addClass("hidden");
        }
    });

    // Fecha de Nacimiento
    $("#id_fecha_nacimiento").on("change input blur", function() {
        if ($(this).val() === "") {
            $("#id_fecha_nacimiento-js-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else {
            let fechaNacimiento = new Date($(this).val());
            let hoy = new Date();
            let edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
            let m = hoy.getMonth() - fechaNacimiento.getMonth();
            if (m < 0 || (m === 0 && hoy.getDate() < fechaNacimiento.getDate())) {
                edad--;
            }
            if (edad < 18) {
                $("#id_fecha_nacimiento-js-error").text("Debes ser mayor de 18 años.").removeClass("hidden");
            } else {
                $("#id_fecha_nacimiento-js-error").addClass("hidden");
            }
        }
    });

    // Dirección
    $("#id_direccion").on("input", function() {
        if ($(this).val().trim() === "") {
            $("#id_direccion-js-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else {
            $("#id_direccion-js-error").addClass("hidden");
        }
    });

    // Rol
    $("#id_rol").on("change", function() {
        if ($(this).val() === "") {
            $("#id_rol-js-error").text("Por favor, selecciona un rol.").removeClass("hidden");
        } else {
            $("#id_rol-js-error").addClass("hidden");
        }
    });

    // Validación del formulario al enviar
    $("#registrationForm").submit(function(event) {
        let formValid = true;
        
        // Ocultar todos los mensajes de error anteriores
        $(".text-red-500.text-xs").addClass("hidden");

        // Validar cada campo
        // Nombre Completo
        if ($("#id_nombre_completo").val().trim() === "") {
            $("#id_nombre_completo-js-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        }

        // Nombre de Usuario
        if ($("#id_nombre_usuario").val().trim() === "") {
            $("#id_nombre_usuario-js-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        }

        // Correo Electrónico
        let emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if ($("#id_correo_electronico").val().trim() === "") {
            $("#id_correo_electronico-js-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else if (!emailRegex.test($("#id_correo_electronico").val().trim())) {
            $("#id_correo_electronico-js-error").text("Por favor, ingresa un correo electrónico válido.").removeClass("hidden");
            formValid = false;
        }

        // Contraseña
        let password = $("#id_contrasena").val();
        let passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]).{8,}$/;
        if (password.trim() === "") {
            $("#id_contrasena-js-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else if (!passwordRegex.test(password)) {
            $("#id_contrasena-js-error").text("La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una letra minúscula, un número y un carácter especial.").removeClass("hidden");
            formValid = false;
        }

        // Repetir Contraseña
        if ($("#id_repetir_contrasena").val().trim() === "") {
            $("#id_repetir_contrasena-js-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else if ($("#id_repetir_contrasena").val() !== password) {
            $("#id_repetir_contrasena-js-error").text("Las contraseñas no coinciden.").removeClass("hidden");
            formValid = false;
        }

        // Número de Teléfono
        let telefono = $("#id_numero_telefono").val().trim();
        let telefonoRegex = /^\d{1,9}$/;
        if (telefono === "") {
            $("#id_numero_telefono-js-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else if (!telefonoRegex.test(telefono)) {
            $("#id_numero_telefono-js-error").text("El número de teléfono debe contener solo números y tener como máximo 9 dígitos.").removeClass("hidden");
            formValid = false;
        }

        // Fecha de Nacimiento
        if ($("#id_fecha_nacimiento").val() === "") {
            $("#id_fecha_nacimiento-js-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else {
            let fechaNacimiento = new Date($("#id_fecha_nacimiento").val());
            let hoy = new Date();
            let edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
            let m = hoy.getMonth() - fechaNacimiento.getMonth();
            if (m < 0 || (m === 0 && hoy.getDate() < fechaNacimiento.getDate())) {
                edad--;
            }
            if (edad < 18) {
                $("#id_fecha_nacimiento-js-error").text("Debes ser mayor de 18 años.").removeClass("hidden");
                formValid = false;
            }
        }

        // Dirección
        if ($("#id_direccion").val().trim() === "") {
            $("#id_direccion-js-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        }

        // Rol
        if ($("#id_rol").val() === "") {
            $("#id_rol-js-error").text("Por favor, selecciona un rol.").removeClass("hidden");
            formValid = false;
        }

        if (!formValid) {
            event.preventDefault(); // Evitar que se envíe el formulario
        }
    });
});