from django.db import models
from django.core.exceptions import ValidationError

class ConfiguracionImpresion(models.Model):
    """
    Un modelo singleton para almacenar la configuración de impresión global.
    Se accede a la configuración a través del método de clase `load()`.
    """
    nombre_empresa = models.CharField(
        max_length=200,
        default="Nombre de tu Empresa",
        help_text="El nombre de la empresa que aparecerá en los documentos."
    )
    logo = models.ImageField(
        upload_to='configuracion/',
        null=True,
        blank=True,
        help_text="Logo que aparecerá en la parte superior de los documentos impresos."
    )
    telefono_empresa = models.CharField(
        max_length=50,
        blank=True,
        help_text="Teléfono de contacto de la empresa."
    )
    email_empresa = models.EmailField(
        blank=True,
        help_text="Correo electrónico de contacto de la empresa."
    )
    pie_de_pagina = models.TextField(
        blank=True,
        help_text="Texto que aparecerá en el pie de página de los documentos impresos."
    )
    # Opciones para mostrar/ocultar secciones del reporte
    mostrar_seccion_garante = models.BooleanField(
        default=True,
        help_text="Si está marcado, se mostrará la información del garante en el reporte."
    )
    mostrar_tabla_amortizacion = models.BooleanField(
        default=True,
        help_text="Si está marcado, se mostrará la tabla de amortización completa."
    )

    class Meta:
        verbose_name = "Configuración de Impresión"
        verbose_name_plural = "Configuración de Impresión"

    def __str__(self):
        return "Configuración de Impresión"

    def save(self, *args, **kwargs):
        # Asegura que este objeto sea siempre el único que exista.
        self.pk = 1
        super(ConfiguracionImpresion, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Previene la eliminación de este objeto.
        pass

    @classmethod
    def load(cls):
        # Método de conveniencia para obtener o crear la única instancia de configuración.
        obj, created = cls.objects.get_or_create(pk=1)
        return obj