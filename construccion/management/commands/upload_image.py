# construccion/management/commands/upload_image.py

import argparse
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os # Para verificar si el archivo existe

class Command(BaseCommand):
    help = 'Sube una imagen local a Cloudinary desde la terminal.'

    def add_arguments(self, parser):
        # Argumento posicional obligatorio: la ruta a la imagen
        parser.add_argument(
            'image_path',
            type=str,
            help='La ruta completa al archivo de imagen que quieres subir.'
        )
        # Argumento opcional: nombre público (public_id) en Cloudinary
        parser.add_argument(
            '--public-id',
            type=str,
            help='(Opcional) El ID público que tendrá la imagen en Cloudinary. Si no se especifica, Cloudinary genera uno aleatorio.',
            default=None
        )
        # Argumento opcional: carpeta en Cloudinary
        parser.add_argument(
            '--folder',
            type=str,
            help='(Opcional) La carpeta dentro de Cloudinary donde se guardará la imagen.',
            default=None
        )

    def handle(self, *args, **options):
        image_path = options['image_path']
        public_id = options['public_id']
        folder = options['folder']

        # 1. Verificar que el archivo de imagen exista
        if not os.path.isfile(image_path):
            raise CommandError(f"El archivo de imagen no se encontró en la ruta: {image_path}")

        # 2. Configurar Cloudinary (usa las credenciales de settings.py)
        #    Aunque ya hay un config global en settings.py, hacerlo aquí es más explícito y robusto para un comando.
        try:
            # Intenta leer directamente las variables hardcoded (ajusta si usas CLOUDINARY_STORAGE)
            cloud_name = settings.CLOUDINARY_CLOUD_NAME
            api_key = settings.CLOUDINARY_API_KEY
            api_secret = settings.CLOUDINARY_API_SECRET

            cloudinary.config(
                cloud_name = cloud_name,
                api_key = api_key,
                api_secret = api_secret,
                secure=True # Usar HTTPS
            )
            self.stdout.write(self.style.NOTICE(f"Configuración de Cloudinary cargada para '{cloud_name}'."))
        except AttributeError as e:
             raise CommandError(f"No se encontró la configuración de Cloudinary directamente en settings.py ({e}). Asegúrate de que CLOUDINARY_CLOUD_NAME, API_KEY, y API_SECRET estén definidos.")

        # 3. Subir la imagen
        self.stdout.write(f"Intentando subir la imagen: {image_path}...")
        try:
            upload_options = {}
            if public_id:
                upload_options['public_id'] = public_id
                # Evita que Cloudinary añada caracteres aleatorios si el public_id ya existe
                upload_options['overwrite'] = True
            else:
                # Usa el nombre del archivo (sin extensión) como public_id si no se especifica uno
                upload_options['use_filename'] = True
                upload_options['unique_filename'] = False # Para evitar caracteres aleatorios si use_filename es True

            if folder:
                upload_options['folder'] = folder

            # Llamada a la API de Cloudinary para subir
            result = cloudinary.uploader.upload(image_path, **upload_options)

            # 4. Mostrar resultado
            self.stdout.write(self.style.SUCCESS(f"¡Imagen subida con éxito!"))
            self.stdout.write(f"  Public ID: {result.get('public_id')}")
            self.stdout.write(f"  URL segura: {result.get('secure_url')}")
            if folder:
                 self.stdout.write(f"  Carpeta: {result.get('folder', folder)}") # Muestra la carpeta confirmada

        except Exception as e:
            # Imprime el error específico de Cloudinary o de la subida
            self.stderr.write(self.style.ERROR(f"Error al subir la imagen a Cloudinary: {e}"))
            # Opcional: raise CommandError para detener con error status
            # raise CommandError(f"Error al subir la imagen a Cloudinary: {e}")