import os
import sys

# Añade la ruta que contiene tu carpeta 'config' al path de Python.
# Esta es la carpeta 'prestamos_project' dentro de tu repositorio.
path = '/home/eugeniosoftware17/Sistema_Prestamos_0.0.1/prestamos_project'
if path not in sys.path:
    sys.path.insert(0, path)

   # Ahora Django sabrá dónde encontrar 'config.settings'
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
   
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()