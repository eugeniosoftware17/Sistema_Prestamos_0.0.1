from django.shortcuts import redirect
from django.urls import reverse
import base64
from django.http import HttpResponse
from django.conf import settings

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Solo aplicamos la lógica para usuarios autenticados que no son staff
        if request.user.is_authenticated and not request.user.is_staff:
            # Evitar bucles de redirección infinitos
            allowed_paths = [
                reverse('client_change_password'), 
                reverse('client_logout')
            ]
            if request.path not in allowed_paths:
                try:
                    cliente = request.user.cliente_profile
                    if cliente.debe_cambiar_contrasena:
                        # Si la bandera está activa, redirigir a la página de cambio de contraseña
                        return redirect('client_change_password')
                except AttributeError:
                    # El perfil del cliente no existe o no tiene el campo, no hacer nada.
                    pass

        return response

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si la autenticación básica no está activada, no hacer nada.
        if not settings.BASIC_AUTH_ENABLED:
            return self.get_response(request)

        # Comprobar si la cabecera de autenticación está presente
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2 and auth[0].lower() == "basic":
                try:
                    # Decodificar las credenciales
                    auth_str = base64.b64decode(auth[1]).decode('utf-8')
                    username, password = auth_str.split(':', 1)
                    
                    # Comparar con las credenciales de la configuración
                    if username == settings.BASIC_AUTH_USER and password == settings.BASIC_AUTH_PASSWORD:
                        return self.get_response(request)
                except (TypeError, UnicodeDecodeError):
                    # Error en la decodificación, denegar acceso
                    return self._deny_access()
        
        # Si no hay cabecera o es inválida, solicitar autenticación
        return self._deny_access()

    def _deny_access(self):
        response = HttpResponse("Acceso no autorizado. Se requiere una llave maestra.", status=401)
        response['WWW-Authenticate'] = 'Basic realm="Acceso Restringido al Sistema de Préstamos"'
        return response
