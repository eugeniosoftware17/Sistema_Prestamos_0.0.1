from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ConfiguracionImpresion
from .forms import ConfiguracionImpresionForm

def es_administrador(user):
    """
    Verifica si un usuario pertenece al grupo 'Administradores' o es superusuario.
    """
    return user.is_staff or user.groups.filter(name='Administradores').exists()

@login_required
@user_passes_test(es_administrador, login_url='/')
def gestionar_configuracion_impresion(request):
    """
    Vista para gestionar la configuración de impresión.
    Permite a los administradores ver y actualizar la configuración.
    """
    # Carga la única instancia de configuración, o la crea si no existe.
    config = ConfiguracionImpresion.load()

    if request.method == 'POST':
        # Si el método es POST, se está enviando el formulario.
        form = ConfiguracionImpresionForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '¡La configuración de impresión ha sido guardada con éxito!')
            # Redirige a la misma página para seguir editando.
            return redirect('configuracion_impresion')
        else:
            messages.error(request, 'Hubo un error al guardar. Por favor, revisa el formulario.')
    else:
        # Si el método es GET, se muestra el formulario con los datos actuales.
        form = ConfiguracionImpresionForm(instance=config)

    context = {
        'form': form,
        'titulo_pagina': 'Configuración de Impresión'
    }
    # La plantilla la crearemos en el siguiente paso.
    return render(request, 'configuracion/gestionar_configuracion.html', context)