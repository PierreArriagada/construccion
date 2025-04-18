$(document).ready(function() {

    if ($("#rol").val() === "") {
        $("#rol-error").text("Por favor, selecciona un rol.").removeClass("hidden");
    }
    $("#registrationForm").submit(function(event) {
        let formValid = true;

        
        $(".text-red-500").addClass("hidden");

        // --- Nombre de la Persona ---
        if ($("#nombrePersona").val().trim() === "") {
            $("#nombrePersona-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        }

        // --- Nombre de Usuario ---
        if ($("#nombreUsuario").val().trim() === "") {
            $("#nombreUsuario-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        }

        // --- Correo Electrónico ---
        let emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if ($("#correoElectronico").val().trim() === "") {
            $("#correoElectronico-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else if (!emailRegex.test($("#correoElectronico").val().trim())) {
            $("#correoElectronico-error").text("Por favor, ingresa un correo electrónico válido.").removeClass("hidden");
            formValid = false;
        }

        // --- Contraseña ---
        let password = $("#contrasena").val();
        let passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]).{8,}$/;
        if (password.trim() === "") {
            $("#contrasena-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else if (!passwordRegex.test(password)) {
            $("#contrasena-error").text("La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una letra minúscula, un número y un carácter especial.").removeClass("hidden");
            formValid = false;
        }

        // --- Repetir Contraseña ---
        if ($("#repetirContrasena").val().trim() === "") {
            $("#repetirContrasena-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else if ($("#repetirContrasena").val() !== password) {
            $("#repetirContrasena-error").text("Las contraseñas no coinciden.").removeClass("hidden");
            formValid = false;
        }

        // --- Número de Teléfono ---
        let telefono = $("#numeroTelefono").val().trim();
        let telefonoRegex = /^\d{1,9}$/;
        if (telefono === "") {
            $("#numeroTelefono-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else if (!telefonoRegex.test(telefono)) {
          $("#numeroTelefono-error").text("El número de teléfono debe contener solo números y tener como máximo 9 dígitos.").removeClass("hidden");
          formValid = false;
        }


        // --- Fecha de Nacimiento ---
        if ($("#fechaNacimiento").val() === "") {
            $("#fechaNacimiento-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        } else {
            let fechaNacimiento = new Date($("#fechaNacimiento").val());
            let hoy = new Date();
            let edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
            let m = hoy.getMonth() - fechaNacimiento.getMonth();
            if (m < 0 || (m === 0 && hoy.getDate() < fechaNacimiento.getDate())) {
                edad--;
            }
            if (edad < 18) {
                $("#fechaNacimiento-error").text("Debes ser mayor de 18 años.").removeClass("hidden");
                formValid = false;
            }
        }

        // --- Dirección ---
        if ($("#direccion").val().trim() === "") {
            $("#direccion-error").text("Este campo es obligatorio.").removeClass("hidden");
            formValid = false;
        }

        // ---- Rol ----
        
        if ($("#rol").val() === "") {
            $("#rol-error").text("Por favor, selecciona un rol.").removeClass("hidden");
            formValid = false;
        }

        if (!formValid) {
            event.preventDefault(); // 
        }
    });

    // --- validacion en timepo real 
    $("#nombreUsuario").on("input", function() {
        if ($(this).val().trim() === "") {
            $("#nombreUsuario-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else {
            $("#nombreUsuario-error").addClass("hidden");
        }
    });

    $("#correoElectronico").on("input", function() {
        let emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if ($(this).val().trim() === "") {
            $("#correoElectronico-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else if (!emailRegex.test($(this).val().trim())) {
            $("#correoElectronico-error").text("Por favor, ingresa un correo electrónico válido.").removeClass("hidden");
        } else {
            $("#correoElectronico-error").addClass("hidden");
        }
    });

    $("#contrasena").on("input", function() {
        let passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]).{8,}$/;
        if ($(this).val().trim() === "") {
            $("#contrasena-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else if (!passwordRegex.test($(this).val())) {
            $("#contrasena-error").text("La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una letra minúscula, un número y un carácter especial.").removeClass("hidden");
        } else {
            $("#contrasena-error").addClass("hidden");
        }
    });

    $("#repetirContrasena").on("input", function() {
        if ($(this).val().trim() === "") {
            $("#repetirContrasena-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else if ($(this).val() !== $("#contrasena").val()) {
            $("#repetirContrasena-error").text("Las contraseñas no coinciden.").removeClass("hidden");
        } else {
            $("#repetirContrasena-error").addClass("hidden");
        }
    });

    $("#numeroTelefono").on("input", function() {
        let telefonoRegex = /^\d{1,9}$/;
        if ($(this).val().trim() === "") {
            $("#numeroTelefono-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else if (!telefonoRegex.test($(this).val())) {
            $("#numeroTelefono-error").text("El número de teléfono debe contener solo números y tener como máximo 9 dígitos.").removeClass("hidden");
        } else {
            $("#numeroTelefono-error").addClass("hidden");
        }
    });

    $("#fechaNacimiento").on("change", function() {
            if ($(this).val() === "") {
            $("#fechaNacimiento-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else {
            let fechaNacimiento = new Date($(this).val());
            let hoy = new Date();
            let edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
            let m = hoy.getMonth() - fechaNacimiento.getMonth();
            if (m < 0 || (m === 0 && hoy.getDate() < fechaNacimiento.getDate())) {
                edad--;
            }
            if (edad < 18) {
                $("#fechaNacimiento-error").text("Debes ser mayor de 18 años.").removeClass("hidden");
            } else {
                $("#fechaNacimiento-error").addClass("hidden");
            }
        }
    });

    $("#direccion").on("input", function() {
        if ($(this).val().trim() === "") {
            $("#direccion-error").text("Este campo es obligatorio.").removeClass("hidden");
        } else {
            $("#direccion-error").addClass("hidden");
        }
    });

    // --- Rol 
    $("#rol").on("change", function() {
        if ($(this).val() === "") {
            $("#rol-error").text("Por favor, selecciona un rol.").removeClass("hidden");
        } else {
            $("#rol-error").addClass("hidden");
        }
    });
});