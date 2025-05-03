# construccion/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.utils import timezone
from .models import Perfil, Rol # importacion de modelos
import re # Para validación regex si es necesaria
from datetime import date
from .models import Producto, Vendido
from django.core.validators import RegexValidator # Importa RegexValidator
import cloudinary


class RegistroForm(forms.Form):
    # --- Definimos las clases de Tailwind para reutilizar ---
    TAILWIND_INPUT_CLASSES = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white leading-tight focus:outline-none focus:shadow-outline'
    TAILWIND_SELECT_CLASSES = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:bg-gray-700 dark:text-white leading-tight focus:outline-none focus:shadow-outline'
    TAILWIND_TEXTAREA_CLASSES = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white leading-tight focus:outline-none focus:shadow-outline'

    # --- Campos del formulario con widgets y clases aplicadas ---

    # Campos correspondientes al modelo User de Django
    nombre_usuario = forms.CharField(
        max_length=20, required=True, label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES})
    )
    correo_electronico = forms.EmailField(
        required=True, label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': TAILWIND_INPUT_CLASSES})
    )
    contrasena = forms.CharField(
        required=True, label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': TAILWIND_INPUT_CLASSES})
    )
    repetir_contrasena = forms.CharField(
        required=True, label="Repetir Contraseña",
        widget=forms.PasswordInput(attrs={'class': TAILWIND_INPUT_CLASSES})
    )

    # Campos correspondientes al modelo Perfil (y datos adicionales)
    nombre_completo = forms.CharField(
        max_length=180, required=True, label="Nombre de la Persona",
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES})
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(), required=True, empty_label="Selecciona un Rol", label="Rol",
        widget=forms.Select(attrs={'class': TAILWIND_SELECT_CLASSES})
    )
    numero_telefono = forms.CharField(
        max_length=15, required=True, label="Número de Teléfono",
        widget=forms.TextInput(attrs={'type':'tel', 'class': TAILWIND_INPUT_CLASSES, 'maxlength':'9'}) # Añadido type y maxlength
    )
    fecha_nacimiento = forms.DateField(
        required=True, label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}) # type='date' para el selector de fecha
    )
    direccion = forms.CharField(
        required=True, label="Dirección",
        widget=forms.Textarea(attrs={'rows': 3, 'class': TAILWIND_TEXTAREA_CLASSES})
    )
    comentarios = forms.CharField(
        required=False, label="Comentarios (Opcional)",
        widget=forms.Textarea(attrs={'rows': 4, 'class': TAILWIND_TEXTAREA_CLASSES})
    )

    # --- Validación ---

    def clean_nombre_usuario(self):
        username = self.cleaned_data['nombre_usuario']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        if len(username) > 20:
             raise ValidationError("El nombre de usuario no puede exceder los 20 caracteres.")
        return username

    def clean_correo_electronico(self):
        email = self.cleaned_data['correo_electronico']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_contrasena(self):
        password = self.cleaned_data['contrasena']
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]).{8,}$'
        if not re.match(password_regex, password):
            raise ValidationError(
                "La contraseña debe tener al menos 8 caracteres, una mayúscula, "
                "una minúscula, un número y un carácter especial."
            )
        return password

    def clean_repetir_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')
        repetir_contrasena = self.cleaned_data.get('repetir_contrasena')
        if contrasena and repetir_contrasena and contrasena != repetir_contrasena:
            raise ValidationError("Las contraseñas no coinciden.")
        return repetir_contrasena

    def clean_numero_telefono(self):
        telefono = self.cleaned_data['numero_telefono']
        if not re.match(r'^\d{9}$', telefono): # Validación estricta de 9 dígitos
            raise ValidationError("El número de teléfono debe contener exactamente 9 dígitos.")
        return telefono

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if edad < 18:
            raise ValidationError("Debes ser mayor de 18 años para registrarte.")
        return fecha_nacimiento

    # --- Método save ---
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['nombre_usuario'],
            email=self.cleaned_data['correo_electronico'],
            password=self.cleaned_data['contrasena']
        )
        perfil = Perfil.objects.create(
            user=user,
            rol=self.cleaned_data['rol'],
            nombre_completo=self.cleaned_data['nombre_completo'],
            telefono=self.cleaned_data['numero_telefono'],
            fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
            direccion=self.cleaned_data['direccion'],
            comentarios=self.cleaned_data['comentarios']
        )
        return user
 

class LoginForm(forms.Form):
    TAILWIND_INPUT_CLASSES = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-600 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
    identificador = forms.CharField(
        label="Nombre de Usuario o Correo Electrónico", max_length=254, required=True,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Usuario o correo@ejemplo.com'
            })
    )
    contrasena = forms.CharField(
        label="Contraseña", required=True,
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': 'Contraseña' # Placeholder opcional
            })
    )

class UserEditForm(forms.ModelForm):
    # Define qué campos del User se pueden editar
    email = forms.EmailField(
        label="Correo Electrónico", required=True,
        widget=forms.EmailInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-white leading-tight focus:outline-none focus:shadow-outline'})
    )
    # se podria  añadir first_name, last_name 
    # first_name = forms.CharField(...)
    # last_name = forms.CharField(...)

    class Meta:
        model = User # Basado en el modelo User
        fields = ['email'] # Lista de campos editables (añade 'first_name', 'last_name' si los incluyes arriba)

# --- Formulario para editar campos del Perfil ---
class ProfileEditForm(forms.ModelForm):
    # Aquí se define los campos para poder añadirles widgets con estilos
    # Si no los redefines, usarán los widgets por defecto.
    TAILWIND_INPUT_CLASSES = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-600 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
    TAILWIND_TEXTAREA_CLASSES = TAILWIND_INPUT_CLASSES

    nombre_completo = forms.CharField(
        max_length=180, required=True, label="Nombre de la Persona",
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES})
    )
    numero_telefono = forms.CharField(
        max_length=9, required=True, label="Número de Teléfono (9 dígitos)",
        widget=forms.TextInput(attrs={'type':'tel', 'class': TAILWIND_INPUT_CLASSES, 'maxlength':'9'})
    )
    fecha_nacimiento = forms.DateField(
        required=True, label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES})
    )
    direccion = forms.CharField(
        required=True, label="Dirección",
        widget=forms.Textarea(attrs={'rows': 3, 'class': TAILWIND_TEXTAREA_CLASSES})
    )
    comentarios = forms.CharField(
        required=False, label="Comentarios (Opcional)",
        widget=forms.Textarea(attrs={'rows': 4, 'class': TAILWIND_TEXTAREA_CLASSES})
    )
    # No incluimos 'user' ni 'rol' aquí, se manejan de otra forma
    # No incluimos 'imagen' aquí, se maneja por separado

    class Meta:
        model = Perfil
        # CORRECTO: Los campos están listados aquí
        fields = ['nombre_completo', 'numero_telefono', 'fecha_nacimiento', 'direccion', 'comentarios']

    # Puedes añadir validaciones 'clean_' aquí si necesitas (ej: revalidar edad)
    fecha_nacimiento = forms.DateField(
    required=True,
    label="Fecha de Nacimiento",
    widget=forms.DateInput(
        format='%Y-%m-%d', # <--- ¡AÑADE ESTA LÍNEA!
        attrs={
            'type': 'date',
            'class': TAILWIND_INPUT_CLASSES # Tus clases existentes
            }
    )
)

    def clean_numero_telefono(self):
        telefono = self.cleaned_data['numero_telefono']
        if not re.match(r'^\d{9}$', telefono):
            raise ValidationError("El número de teléfono debe contener exactamente 9 dígitos.")
        return telefono
    


# --- AJUSTA ESTAS CLASES ---
# Asegúrate de que 'border', 'border-black', y 'dark:border-white' estén presentes.
# Puedes ajustar otros estilos como padding (py-2 px-3), focus rings (focus:...), etc.
TAILWIND_INPUT_CLASSES = 'shadow-sm appearance-none border border-black dark:border-white rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-gray-300 dark:focus:ring-offset-gray-800 dark:focus:ring-indigo-600 dark:focus:border-indigo-600'

# Clases para Textarea (puedes añadir más como h-32 para altura)
TAILWIND_TEXTAREA_CLASSES = TAILWIND_INPUT_CLASSES + ' h-32'

# Clases para NumberInput (usualmente las mismas que text input)
TAILWIND_NUMBERINPUT_CLASSES = TAILWIND_INPUT_CLASSES

# Clases para FileInput (pueden ser diferentes, pero aplicamos borde también)
TAILWIND_FILEINPUT_CLASSES = 'block w-full text-sm text-gray-900 border border-black dark:border-white rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:placeholder-gray-400'

# --- FORMULARIOS USANDO LAS CLASES ACTUALIZADAS ---

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['titulo', 'precio', 'imagen', 'comentarios']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'precio': forms.NumberInput(attrs={'class': TAILWIND_NUMBERINPUT_CLASSES}),
            'imagen': forms.ClearableFileInput(attrs={'class': TAILWIND_FILEINPUT_CLASSES}),
            'comentarios': forms.Textarea(attrs={'class': TAILWIND_TEXTAREA_CLASSES}),
        }

    # Método para hacer imagen opcional en edición (importante)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and 'imagen' in self.fields:
             self.fields['imagen'].required = False


class VendidoForm(forms.ModelForm):
    class Meta:
        model = Vendido
        fields = ['titulo', 'precio', 'imagen'] # Ajusta campos si es necesario
        widgets = {
            'titulo': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
            'precio': forms.NumberInput(attrs={'class': TAILWIND_NUMBERINPUT_CLASSES}),
            'imagen': forms.ClearableFileInput(attrs={'class': TAILWIND_FILEINPUT_CLASSES}),
        }

    # Método para hacer imagen opcional en edición (importante)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and 'imagen' in self.fields:
             self.fields['imagen'].required = False

class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto_form.html'
    success_url = reverse_lazy('productAdmin')

class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto_form.html'
    success_url = reverse_lazy('productAdmin')

TAILWIND_INPUT_CLASSES = 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600'

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico')

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label='Nueva Contraseña',
        validators=[
            RegexValidator(
                regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&_-]{8,}$',
                message='La contraseña debe tener al menos 8 caracteres, incluyendo una minúscula, una mayúscula, un número y un carácter especial.',
            )
        ]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': TAILWIND_INPUT_CLASSES}),
        label='Confirmar Nueva Contraseña'
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

