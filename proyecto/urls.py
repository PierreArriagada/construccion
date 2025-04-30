
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.contrib.auth import views as auth_views
from construccion import views #cambio de nombre de app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('forgotPass/', views.forgotPass, name='forgotPass'),
    path('formUser/', views.formUser, name='formUser'),
    path('loginCompany/', views.loginCompany, name='loginCompany'),
    path('loginUser/', views.loginUser, name='loginUser'),
    path('profileUser/', views.profileUser, name='profileUser'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('contacto/', views.contacto, name='contacto'),
    path('editPerfil/', views.editPerfil, name='editPerfil'),
    path('productAdmin', views.productAdmin, name='productAdmin'),
    path('producto_create/', views.producto_create, name='producto_create'),
    path('vendido_create/', views.vendido_create, name='vendido_create'),
    path('producto_form/', views.producto_form, name='producto_form'),
    path('vendido_form/', views.vendido_form, name='vendido_form'),
    path('forgotPass/', views.forgotPass, name='forgotPass'),
    path('resetPass/', views.resetPassForm, name='resetPass'), # URL para el formulario de nueva contraseña
    path('', include('construccion.urls')), # Incluye construccion.urls aquí
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)