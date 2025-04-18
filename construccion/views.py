import traceback
from .models import Producto, Vendido, Perfil, Rol
from .forms import ProductoForm, VendidoForm #crear los forms
from .forms import RegistroForm, LoginForm, UserEditForm, ProfileEditForm
from django.shortcuts import render,redirect
from django.templatetags.static import static 
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages  
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django import forms
from .forms import ForgotPasswordForm, ResetPasswordForm 


import json


from django.shortcuts import render


def index(request):
    # Obtiene todos los productos de la base de datos
    productos = Producto.objects.all()

    # Obtiene todos los vendidos de la base de datos
    vendidos = Vendido.objects.all()

    context = {
        'vendidos': vendidos,
        'productos': productos,  # Usa 'productos' en lugar de 'pedidos'
    }

    return render(request, 'Index.html', context)

def forgotPass(request):
    print("\n[DEBUG forgotPass] Vista iniciada.") # 1. Inicio de la vista
    if request.method == 'POST':
        print("[DEBUG forgotPass] Método POST detectado.") # 2. Es POST
        form = ForgotPasswordForm(request.POST)
        print("[DEBUG forgotPass] Formulario instanciado con POST data.") # 3. Formulario creado
        if form.is_valid():
            print("[DEBUG forgotPass] form.is_valid() = True.") # 4. Formulario es válido (formato email OK)
            email = form.cleaned_data['email']
            print(f"[DEBUG forgotPass] Email extraído: {email}") # 5. Email obtenido
            try:
                print("[DEBUG forgotPass] Intentando User.objects.get(email=...)") # 6. Buscando usuario
                user = User.objects.get(email=email)
                print(f"[DEBUG forgotPass] Usuario encontrado: {user.username}") # 7. Usuario encontrado (Email VÁLIDO)

                # Email VÁLIDO: Guarda en sesión y redirige
                print("[DEBUG forgotPass] Intentando guardar email en sesión...") # 8. Guardando en sesión
                request.session['reset_email'] = email
                # Forzar guardado de sesión por si acaso (normalmente no necesario)
                # request.session.save()
                print(f"[DEBUG forgotPass] Email '{request.session.get('reset_email')}' guardado en sesión (verificar).") # 9. Confirmar guardado (leer de vuelta)
                print("[DEBUG forgotPass] Redirigiendo a 'resetPass'...") # 10. Intentando redirigir
                return redirect('resetPass') # <-- REDIRECCIÓN SI ES VÁLIDO

            except User.DoesNotExist:
                # Email INVÁLIDO: Añade error al form
                print("[DEBUG forgotPass] User.DoesNotExist - Email inválido.") # 7b. Usuario NO encontrado
                form.add_error('email', 'No existe ningún usuario con este correo electrónico.')
                print("[DEBUG forgotPass] Error añadido al formulario.") # 8b. Error añadido
                # La ejecución continúa hacia abajo para renderizar el form con error

        else:
             print("[DEBUG forgotPass] form.is_valid() = False. Errores:", form.errors) # 4b. Formulario inválido

        # Si form no es válido O si email no existe, renderiza DE NUEVO forgotPass CON el form que tiene los errores
        print("[DEBUG forgotPass] Renderizando forgotPass.html (porque form era inválido o user no existe)") # 11. Renderizando de nuevo
        return render(request, 'forgotPass.html', {'form': form}) # Asegúrate que la ruta de la plantilla es correcta

    else: # GET
        print("[DEBUG forgotPass] Método GET detectado.") # 2c. Es GET
        form = ForgotPasswordForm()
        print("[DEBUG forgotPass] Formulario vacío instanciado.") # 3c. Form vacío
        print("[DEBUG forgotPass] Renderizando forgotPass.html (para mostrar form inicial)") # 4c. Renderizando inicial
        return render(request, 'forgotPass.html', {'form': form}) # Asegúrate que la ruta de la plantilla es correcta

# --- VISTA resetPassForm CON PRINTS DETALLADOS ---
def resetPassForm(request):
    print("\n[DEBUG resetPassForm] Vista iniciada.") # 1. Inicio
    # Recupera el email de la sesión
    print("[DEBUG resetPassForm] Intentando obtener 'reset_email' de la sesión...") # 2. Obteniendo sesión
    email = request.session.get('reset_email')
    print(f"[DEBUG resetPassForm] Valor de 'reset_email' en sesión: {email}") # 3. VALOR OBTENIDO (¡CLAVE!)

    # Si no hay email en la sesión, redirige al inicio del proceso
    if not email:
        print("[DEBUG resetPassForm] 'reset_email' es None o vacío. Redirigiendo a 'forgotPass'.") # 4. Email no encontrado -> Redirige
        return redirect('forgotPass')

    print(f"[DEBUG resetPassForm] Email válido encontrado en sesión: {email}. Continuando...") # 5. Email OK, sigue

    success_message = None

    if request.method == 'POST':
        print("[DEBUG resetPassForm] Método POST detectado.") # 6. Es POST
        form = ResetPasswordForm(request.POST) # Asegúrate que el nombre del form es correcto
        print("[DEBUG resetPassForm] Formulario ResetPasswordForm instanciado con POST data.") # 7. Form creado
        if form.is_valid():
            print("[DEBUG resetPassForm] form.is_valid() = True.") # 8. Form válido (contraseñas coinciden, etc.)
            # Usa el nombre correcto del campo del formulario (ajústalo si es necesario)
            new_password = form.cleaned_data.get('new_password') or form.cleaned_data.get('new_password1')
            print("[DEBUG resetPassForm] Nueva contraseña extraída.") # 9. Pass obtenida
            try:
                print(f"[DEBUG resetPassForm] Intentando User.objects.get(email={email}) para actualizar...") # 10. Buscando usuario
                user = User.objects.get(email=email)
                print(f"[DEBUG resetPassForm] Usuario encontrado: {user.username}. Estableciendo nueva contraseña...") # 11. User encontrado
                user.set_password(new_password)
                user.save()
                print("[DEBUG resetPassForm] Contraseña actualizada y usuario guardado.") # 12. Guardado

                # Limpia la sesión
                print("[DEBUG resetPassForm] Intentando eliminar 'reset_email' de la sesión...") # 13. Limpiando sesión
                if 'reset_email' in request.session:
                    del request.session['reset_email']
                    # request.session.save() # Podría ser necesario si hay problemas
                    print("[DEBUG resetPassForm] 'reset_email' eliminado de la sesión.") # 14. Eliminado
                else:
                     print("[DEBUG resetPassForm] 'reset_email' no estaba en la sesión para eliminar.")

                success_message = "¡Tu contraseña ha sido cambiada con éxito! Ya puedes iniciar sesión."
                print("[DEBUG resetPassForm] Mensaje de éxito establecido.") # 15. Mensaje éxito listo

                # Renderiza con mensaje de éxito y sin formulario
                print("[DEBUG resetPassForm] Renderizando resetPass.html con mensaje de éxito.") # 16. Render éxito
                return render(request, 'resetPass.html', {'success_message': success_message, 'form': None}) # Ruta plantilla!

            except User.DoesNotExist:
                print(f"[DEBUG resetPassForm] ERROR INESPERADO: User.DoesNotExist para email {email} durante el reseteo.") # 11b. Error raro
                if 'reset_email' in request.session:
                    del request.session['reset_email']
                print("[DEBUG resetPassForm] Redirigiendo a 'forgotPass' por seguridad.") # 12b. Redirige error
                return redirect('forgotPass')
        else:
            # Si el form no es válido (ej: contraseñas no coinciden)
            print("[DEBUG resetPassForm] form.is_valid() = False. Errores:", form.errors) # 8b. Form inválido
            print("[DEBUG resetPassForm] Renderizando resetPass.html con formulario inválido.") # 17. Render form inválido
            return render(request, 'resetPass.html', {'form': form}) # Ruta plantilla!

    else: # Método GET
        print("[DEBUG resetPassForm] Método GET detectado.") # 6c. Es GET
        form = ResetPasswordForm() # Asegúrate que el nombre del form es correcto
        print("[DEBUG resetPassForm] Formulario vacío ResetPasswordForm instanciado.") # 7c. Form vacío
        print("[DEBUG resetPassForm] Renderizando resetPass.html (para mostrar form de reseteo inicial)") # 8c. Render inicial
        return render(request, 'resetPass.html', {'form': form}) # Ruta plantilla!

def productAdmin(request):
    productos = Producto.objects.all()
    vendidos = Vendido.objects.all()
    return render(request, 'productAdmin.html', {'productos': productos, 'vendidos': vendidos})

def vendido_form(request):
    return render(request, 'vendido_form.html')

def producto_form(request):
    return render(request, 'producto_form.html')


def formUser(request):
    registro_exitoso = False
    # Inicializa form fuera del if/else para que siempre exista en el contexto final
    # si el método es GET, será un form vacío, si es POST, será el form con datos/errores
    if request.method == 'GET':
        form = RegistroForm()
    else: # POST
        form = RegistroForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            try:
                print("--- Formulario válido. Intentando guardar... ---") # Mensaje para depuración en consola
                user = form.save() # Intenta crear User y Perfil
                print(f"--- Usuario '{user.username}' y Perfil creados exitosamente en BD. ---") # Mensaje para depuración

                # Solo si save() tuvo éxito completo:
                messages.success(request, '¡Tu cuenta ha sido creada exitosamente!')
                registro_exitoso = True
                # login(request, user) # Opcional: Comenta si rediriges a login

                # Preparamos contexto para mostrar estado de éxito
                context = {
                    'registro_exitoso': True,
                    'form': RegistroForm() # Formulario vacío para limpiar campos
                }
                return render(request, 'formUser.html', context) # Renderiza en estado éxito

            except Exception as e:
                # ¡ERROR DURANTE EL GUARDADO!
                print("\n!!! ERROR AL EJECUTAR form.save() !!!") # Mensaje para depuración en consola
                # Imprime el traceback completo en la consola donde corre 'runserver'
                traceback.print_exc()
                # Añade un mensaje de error más útil para el usuario
                messages.error(request, f'Ocurrió un error interno al guardar ({type(e).__name__}). Por favor, inténtalo de nuevo o contacta soporte.')
                registro_exitoso = False
                # Mantenemos el 'form' actual (que era válido pero falló al guardar)
                # para mostrarlo de nuevo al usuario.
        else:
            # El formulario NO es válido
            messages.error(request, 'Hubo errores en el formulario. Por favor, corrígelos.')
            registro_exitoso = False
            # Mantenemos el 'form' actual (que contiene los errores de validación)

    # Contexto para la renderización final (GET o POST con errores)
    context = {
        'form': form,
        'registro_exitoso': registro_exitoso
    }
    return render(request, 'formUser.html', context)

def loginCompany(request):
    return render(request, 'loginCompany.html')

def loginUser(request):
    if request.user.is_authenticated:
        # -- Redirección si ya está logueado (AÑADIMOS LÓGICA DE ROL AQUÍ TAMBIÉN) --
        try:
            rol_nombre = request.user.perfil.rol.nombre # Asume related_name='perfil'
            if rol_nombre == 'Administrador':
                # Si un admin ya logueado intenta ir a login, lo mandamos a gestionar productos
                return redirect('productAdmin') # Usa el name= de tu URL de gestión
            else:
                # Otros roles van a su perfil
                return redirect('profileUser')
        except (Perfil.DoesNotExist, AttributeError):
            # Si hay problemas con perfil/rol, envía a un lugar seguro (ej: logout o index)
             # Quizás mejor hacer logout si el estado es inconsistente
             logout(request)
             messages.warning(request, 'Hubo un problema con tu perfil, sesión cerrada.')
             return redirect('loginUser') # Vuelve a login

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identificador = form.cleaned_data['identificador']
            password = form.cleaned_data['contrasena']
            user = None
            # ... (Tu lógica de autenticación con username y/o email - SIN CAMBIOS) ...
            user = authenticate(request, username=identificador, password=password)
            if user is None:
                try:
                    user_by_email = User.objects.get(email=identificador)
                    user = authenticate(request, username=user_by_email.username, password=password)
                except User.DoesNotExist:
                    pass

            # --- AQUÍ EMPIEZA LA MODIFICACIÓN PARA REDIRECCIÓN POR ROL ---
            if user is not None:
                login(request, user)
                messages.info(request, f'Bienvenido de nuevo, {user.username}!')
                # Intentamos obtener el rol del usuario
                try:
                    # Accedemos al rol a través del perfil asociado al usuario
                    rol_nombre = user.perfil.rol.nombre
                    # Comparamos el nombre del rol
                    if rol_nombre == 'Administrador':
                        # Si es Administrador, redirige a la gestión de productos
                        return redirect('productAdmin') # Usa el name= de la URL de gestión
                    else:
                        # Cualquier otro rol (Usuario, Bodeguero, etc.) va a su perfil
                        return redirect('profileUser') # Usa el name= de la URL de perfil
                except (Perfil.DoesNotExist, AttributeError):
                     # Si el usuario no tiene perfil o el perfil no tiene rol asignado
                     messages.warning(request, 'No se pudo determinar tu rol o perfil. Contacta soporte.')
                     # Decide a dónde enviar en este caso raro, quizás logout o una página genérica
                     logout(request) # Es más seguro cerrar sesión si el estado es inválido
                     return redirect('loginUser') # Vuelve a login
                except Rol.DoesNotExist:
                     # Si el perfil apunta a un ID de rol que ya no existe
                     messages.warning(request, 'Tu rol asignado no es válido. Contacta soporte.')
                     logout(request)
                     return redirect('loginUser')

            else: # user is None (Autenticación fallida)
                messages.error(request, 'Nombre de usuario/correo o contraseña incorrectos.')
                # Cae al render final con el form (sin errores específicos aquí)
        else: # form is not valid
            messages.error(request, 'Por favor, ingresa tu identificador y contraseña.')
            # Cae al render final con el form que contiene errores de campo
    else: # GET request
        form = LoginForm()

    # Contexto para renderizar si es GET o si POST falló (validación o autenticación)
    context = {'form': form}
    return render(request, 'loginUser.html', context) # Ajusta ruta si es necesario


# --- Vista de Logout (sin cambios, ya estaba bien) ---
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('loginUser')


# --- (Necesario) Tu vista de perfil (ejemplo mínimo) ---
@login_required
def ver_perfil(request):
    # Asume que tienes un modelo Perfil vinculado a User
    # perfil = request.user.perfil # Si tienes related_name='perfil'
    # O busca el perfil:
    from .models import Perfil
    try:
        perfil = Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
        perfil = None # O maneja el caso como prefieras

    context = {'perfil': perfil}
    return render(request, 'profileUser', context) # La plantilla del perfil

@login_required # <-- ESENCIAL: Solo usuarios logueados pueden ver esto
def profileUser(request):
    try:
        # Busca el objeto Perfil que está vinculado al usuario logueado (request.user)
        # Esta es la línea que conecta User con Perfil y obtiene los datos de construccion_perfil
        perfil_obj = Perfil.objects.get(user=request.user)
        # Alternativa si tienes related_name='perfil' en models.py:
        # perfil_obj = request.user.perfil
    except Perfil.DoesNotExist:
        # Si por alguna razón no existe el perfil para este usuario
        messages.error(request, 'Error: No se encontró un perfil asociado a tu usuario.')
        perfil_obj = None # Pasa None a la plantilla
    except Exception as e:
        # Otros posibles errores
        messages.error(request, f'Error al cargar el perfil: {e}')
        perfil_obj = None

    # Prepara el diccionario de contexto para enviar datos a la plantilla
    context = {
        'user': request.user,   # Pasa el objeto User estándar
        'perfil': perfil_obj  # Pasa el objeto Perfil encontrado (o None si hubo error)
    }

    # Renderiza la plantilla HTML pasándole el contexto
    # Asegúrate que la ruta 'construccion/profileUser.html' sea correcta
    return render(request, 'profileUser.html', context)

@login_required
def editPerfil(request):
    try:
        perfil_obj = request.user.perfil # Asume related_name='perfil' o usa Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
         messages.error(request, 'Perfil no encontrado.')
         return redirect('profileUser') # O a donde quieras

    if request.method == 'POST':
        # Crea instancias de los forms con los datos enviados Y las instancias originales
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, instance=perfil_obj)

        # Valida ambos formularios
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()    # Guarda cambios en User (auth_user)
            profile_form.save() # Guarda cambios en Perfil (construccion_perfil)
            messages.success(request, '¡Tu perfil ha sido actualizado correctamente!')
            return redirect('profileUser') # Vuelve a la vista de perfil
        else:
            messages.error(request, 'Por favor corrige los errores indicados.')
    else: # Petición GET
        # Crea instancias de los forms con los datos actuales del usuario y perfil
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=perfil_obj)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    # Necesitas una plantilla HTML para este formulario de edición
    return render(request, 'editPerfil.html', context)

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        try:
            return self.request.user.perfil.rol.nombre == 'Administrador'
        except (Perfil.DoesNotExist, AttributeError, Rol.DoesNotExist):
            return False

    def handle_no_permission(self):
        messages.error(self.request, 'Acceso denegado. No tienes permisos de administrador.')
        try:
            profile_url = reverse_lazy('profileUser') # O 'perfil_usuario'
        except:
            profile_url = reverse_lazy('loginUser')
        return redirect(profile_url)


class ProductoListView(AdminRequiredMixin, ListView):
    model = Producto
    template_name = 'DOM/producto_list.html' # <- Necesitaremos esta plantilla
    context_object_name = 'productos'
    paginate_by = 10

class ProductoCreateView(AdminRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'DOM/producto_form.html' # <- Necesitaremos esta plantilla
    success_url = reverse_lazy('productAdmin') #Cambio a productAdmin

    def form_valid(self, form):
        messages.success(self.request, f'Producto "{form.instance.titulo}" creado exitosamente.')
        return super().form_valid(form)

class ProductoUpdateView(AdminRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'DOM/producto_form.html' # <- Reutiliza plantilla de form
    success_url = reverse_lazy('productAdmin') #Cambio a productAdmin

    def form_valid(self, form):
        messages.success(self.request, f'Producto "{form.instance.titulo}" actualizado exitosamente.')
        return super().form_valid(form)

class ProductoDeleteView(AdminRequiredMixin, DeleteView):
    model = Producto
    success_url = reverse_lazy('productAdmin')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f'Producto "{self.get_object().titulo}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class ProductoDeleteView(AdminRequiredMixin, DeleteView):
    model = Producto
    success_url = reverse_lazy('productAdmin')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Producto "{self.object.titulo}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)



# --- Vistas CRUD para Vendidos (SOLO ADMIN) ---

class VendidoListView(AdminRequiredMixin, ListView):
    model = Vendido
    template_name = 'DOM/vendido_list.html'
    context_object_name = 'vendidos'
    paginate_by = 10

class VendidoCreateView(AdminRequiredMixin, CreateView):
    model = Vendido
    form_class = VendidoForm
    template_name = 'DOM/vendido_form.html'
    success_url = reverse_lazy('productAdmin') #Cambio a productAdmin

    def form_valid(self, form):
        messages.success(self.request, f'Vendido "{form.instance.titulo}" creado exitosamente.')
        return super().form_valid(form)

class VendidoUpdateView(AdminRequiredMixin, UpdateView):
    model = Vendido
    form_class = VendidoForm
    template_name = 'DOM/vendido_form.html'
    success_url = reverse_lazy('productAdmin') #Cambio a productAdmin

    def form_valid(self, form):
        messages.success(self.request, f'Vendido "{form.instance.titulo}" actualizado exitosamente.')
        return super().form_valid(form)

class VendidoDeleteView(AdminRequiredMixin, DeleteView):
    model = Vendido
    success_url = reverse_lazy('productAdmin')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Vendido "{self.object.titulo}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

  
TAILWIND_INPUT_CLASSES = 'shadow-sm appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white dark:border-gray-600 dark:focus:ring-indigo-600 dark:focus:border-indigo-600'
TAILWIND_TEXTAREA_CLASSES = TAILWIND_INPUT_CLASSES + ' h-32'
TAILWIND_FILEINPUT_CLASSES = 'block w-full text-sm text-white border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-white focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'

def vendido_create(request):
    if request.method == 'POST':
        form = VendidoForm(request.POST, request.FILES)
        if form.is_valid():
            vendido = form.save(commit=False)
            vendido.user = request.user
            vendido.save()
            messages.success(request, '¡Vendido creado exitosamente!')
            return redirect('productAdmin')
    else:
        form = VendidoForm()
    return render(request, 'DOM/vendido_form.html', {'form': form})

def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.user = request.user
            producto.save()
            messages.success(request, '¡Producto creado exitosamente!')
            return redirect('productAdmin')
    else:
        form = ProductoForm()
    return render(request, 'DOM/producto_form.html', {'form': form})
