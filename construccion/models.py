from django.db import models
from django.contrib.auth.models import User # Importa el modelo User estándar de Django
from cloudinary.models import CloudinaryField

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    nombre_completo = models.CharField(max_length=180)
    
    # Cambia ImageField por CloudinaryField
    imagen = CloudinaryField('imagen_perfil', folder='perfiles', null=True, blank=True)
    
    telefono = models.CharField(max_length=15, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    comentarios = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.rol.nombre}"

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

# Modelo para la tabla Productos
class Producto(models.Model):
    titulo = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Cambia ImageField por CloudinaryField
    imagen = CloudinaryField('imagen_producto', folder='productos', null=True, blank=True)
    
    comentarios = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

# Modelo para la tabla Vendidos
class Vendido(models.Model):
    titulo = models.CharField(max_length=200)
    precio = models.CharField(max_length=50, help_text="Precio de venta (puede ser rango o texto)")
    
    # Cambia ImageField por CloudinaryField
    imagen = CloudinaryField('imagen_vendido', folder='vendidos', null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Vendido"
        verbose_name_plural = "Vendidos"