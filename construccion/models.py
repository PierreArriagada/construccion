from django.db import models
from django.contrib.auth.models import User # Importa el modelo User estándar de Django

# Modelo para los Roles de Usuario
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej: Administrador, Usuario, Bodeguero")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

# Modelo para el Perfil de Usuario (extiende User y asigna Rol)
class Perfil(models.Model):
    # --- Conexión con User y Rol ---
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)

    # --- Campos Adicionales del Formulario de Registro ---
    # 'nombre de la persona(180 caracteres)' -> Mapeado aquí
    nombre_completo = models.CharField(max_length=180)

    # 'imagen' -> ImageField para subir archivos. Requiere Pillow (pip install Pillow)
    # null=True, blank=True porque se sube DESPUÉS de crear la cuenta.
    imagen = models.ImageField(upload_to='perfiles/', null=True, blank=True)

    # 'numero de teléfono (máximo 10 números)' -> CharField es más flexible para formatos
    telefono = models.CharField(max_length=15, null=True, blank=True) # +569... etc

    # 'fecha de nacimiento es en dd-mm-aaa' -> DateField almacena la fecha. El formato es para el frontend.
    fecha_nacimiento = models.DateField(null=True, blank=True)

    # 'dirección' -> TextField para direcciones largas
    direccion = models.TextField(null=True, blank=True)

    # 'comentarios' -> TextField para notas generales del usuario
    comentarios = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.rol.nombre}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    # Nota: Los campos 'nombre de usuarios' (username), 'correo electrónico' (email)
    # y 'contraseña' (password) son manejados directamente por el modelo User de Django.
    # El 'rol' se maneja con la ForeignKey a Rol.


# Modelo para la tabla Productos
class Producto(models.Model):
    # 'nombre producto'
    titulo = models.CharField(max_length=200) # O nombre en lugar de titulo si prefieres
    # 'precio'
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    # 'imagen' -> Usamos ImageField también aquí
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    # 'cantidad comentarios, number'
    comentarios = models.IntegerField(default=0) # Asumo que es un contador

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

# Modelo para la tabla Vendidos
class Vendido(models.Model):
    # 'nombre producto'
    titulo = models.CharField(max_length=200)
    # 'precio' -> ¡¡OJO!! Basado en tu ejemplo anterior ('$5M-10M'), esto parece TEXTO.
    # Si en Oracle es VARCHAR2, CharField está bien.
    # Si en Oracle es NUMBER, DEBES usar DecimalField o IntegerField aquí.
    # Revisa tu tabla Oracle y ajusta este tipo si es necesario. Dejaré CharField por ahora.
    precio = models.CharField(max_length=50, help_text="Precio de venta (puede ser rango o texto)")
    # 'imagen' -> Usamos ImageField
    imagen = models.ImageField(upload_to='vendidos/', null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Vendido"
        verbose_name_plural = "Vendidos"
