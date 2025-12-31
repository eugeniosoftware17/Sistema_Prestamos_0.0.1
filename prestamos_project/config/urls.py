"""
Configuración de URLs principal del proyecto.

Aquí se definen las rutas de más alto nivel. Cada ruta se asocia con una vista
o con otro archivo de configuración de URLs de una app específica.
"""
from django.contrib import admin
from django.urls import path, include
# Se importan las vistas de Login y Logout que Django ya trae incorporadas.
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # Ruta para el panel de administración de Django.
    path('admin/', admin.site.urls),
    
    # --- Rutas de Autenticación ---
    # Cuando un usuario visita /login/, se le mostrará la vista de Login de Django.
    # `template_name` le dice a la vista qué archivo HTML debe usar para mostrar el formulario.
    # `name='login'` nos permite referirnos a esta URL desde las plantillas con `{% url 'login' %}`.
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # La vista LogoutView no necesita una plantilla, ya que solo cierra la sesión y redirige.
    # La redirección se configura en settings.py (LOGOUT_REDIRECT_URL).
    path('logout/', LogoutView.as_view(), name='logout'),

    # URL para las búsquedas de autocompletado de django-select2
    path('select2/', include('django_select2.urls')),
    
    # --- Rutas de la Aplicación ---
    # Incluye las URLs para el nuevo módulo de configuración.
    path('configuracion/', include('configuracion.urls')),

    # Incluye todas las URLs definidas en el archivo `urls.py` de la app `dashboard`.
    # Esto mantiene el proyecto organizado, ya que cada app gestiona sus propias URLs.
    path('', include('dashboard.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

# Añade la URL de los archivos multimedia solo en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

