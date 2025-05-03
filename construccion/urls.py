# construccion/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... otras URLs de tu app construccion ...
    path('productos/editar/<int:pk>/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/eliminar/<int:pk>/', views.ProductoDeleteView.as_view(), name='producto_delete'),
    path('vendidos/editar/<int:pk>/', views.VendidoUpdateView.as_view(), name='vendido_update'),
    path('vendidos/eliminar/<int:pk>/', views.VendidoDeleteView.as_view(), name='vendidos_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 