from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, UniqueConstraint
from decimal import Decimal
from django.utils import timezone

# ==================================================
# === MODELO TIPO DE GASTO ===
# ==================================================
# Almacena las categorías de los gastos operativos.
class TipoGasto(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Tipo de Gasto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'prestamos_tipo_gasto'
        verbose_name = "Tipo de Gasto"
        verbose_name_plural = "Tipos de Gastos"


# ==================================================
# === MODELO GASTO PRESTAMO ===
# ==================================================
# Almacena los gastos específicos asociados a un préstamo.
class GastoPrestamo(models.Model):
    prestamo = models.ForeignKey('Prestamo', on_delete=models.CASCADE, related_name="gastos_asociados")
    tipo_gasto = models.ForeignKey(TipoGasto, on_delete=models.PROTECT, verbose_name="Tipo de Gasto")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto del Gasto")
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción Adicional")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_gasto.nombre} - {self.prestamo}"

    class Meta:
        db_table = 'prestamos_gasto_prestamo'
        verbose_name = "Gasto del Préstamo"
        verbose_name_plural = "Gastos del Préstamo"



# ==================================================
# === MODELO CLIENTE ===
# ==================================================
# Almacena la información personal de cada prestatario.
class Cliente(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('cedula', 'Cédula'),
        ('pasaporte', 'Pasaporte'),
    ]

    # Relación con el modelo de usuario de Django para la autenticación
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cliente_profile')

    # Campo para forzar el cambio de contraseña en el primer login
    debe_cambiar_contrasena = models.BooleanField(default=True)

    # CharField es para campos de texto cortos. `max_length` es obligatorio.
    # `verbose_name` es el nombre legible que se mostrará en el panel de administración de Django.
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    
    tipo_documento = models.CharField(
        max_length=10, 
        choices=TIPO_DOCUMENTO_CHOICES, 
        default='cedula', 
        verbose_name="Tipo de Documento"
    )
    numero_documento = models.CharField(max_length=20, unique=True, verbose_name="Número de Documento")
    
    # TextField es para campos de texto largos. `blank=True` y `null=True` hacen que el campo sea opcional.
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico", null=True, blank=True) # Campo añadido
    
    # DateTimeField guarda una fecha y hora. `auto_now_add=True` establece automáticamente la fecha y hora
    # de creación cuando se registra un nuevo cliente.
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    # Nuevos campos
    ESTADO_CIVIL_CHOICES = [
        ('soltero', 'Soltero/a'),
        ('casado', 'Casado/a'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a'),
    ]
    SEXO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
    ]

    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True, verbose_name="Estado Civil")
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, blank=True, null=True, verbose_name="Sexo")
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    apodo = models.CharField(max_length=50, blank=True, null=True, verbose_name="Apodo")

    # Información laboral
    nombre_empresa = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre de la Empresa")
    cargo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cargo o Posición")
    telefono_trabajo = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono del Trabajo")
    ingresos_mensuales = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Ingresos Mensuales")
    fecha_ingreso_trabajo = models.DateField(blank=True, null=True, verbose_name="Fecha de Ingreso al Trabajo")
    trabajo_actual = models.BooleanField(default=True, verbose_name="¿Es su trabajo actual?")

    # El método `__str__` le dice a Django cómo "imprimir" un objeto Cliente.
    # Es muy útil en el panel de administración para ver una representación legible de cada cliente.
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    # La clase Meta permite configurar metadatos para el modelo.
    class Meta:
        db_table = 'prestamos_cliente'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

# ==================================================
# === MODELO GARANTE ===
# ==================================================
# Almacena la información del garante de un préstamo.
class Garante(models.Model):
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula")
    lugar_trabajo = models.CharField(max_length=200, verbose_name="Lugar de Trabajo")
    ingresos_mensuales = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ingresos Mensuales")

    def __str__(self):
        return self.nombre_completo

    class Meta:
        db_table = 'prestamos_garante'
        verbose_name = "Garante"
        verbose_name_plural = "Garantes"


# ==================================================
# === MODELO TIPO DE PRÉSTAMO ===
# ==================================================
class TipoPrestamo(models.Model):
    METODO_CALCULO_CHOICES = [
        ('frances', 'Francés (cuota fija)'),
        # Futuros métodos:
        # ('aleman', 'Alemán (capital fijo)'),
        # ('simple', 'Interés Simple'),
    ]
    PERIODO_TASA_CHOICES = [
        ('anual', 'Anual'),
        ('mensual', 'Mensual'),
    ]

    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Tipo de Préstamo")
    tasa_interes_predeterminada = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Tasa de Interés Predeterminada (%)")
    periodo_tasa = models.CharField(max_length=10, choices=PERIODO_TASA_CHOICES, default='anual', verbose_name="Periodo de la Tasa")
    monto_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Monto Mínimo")
    monto_maximo = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Máximo")
    plazo_minimo_meses = models.IntegerField(default=1, verbose_name="Plazo Mínimo en Meses")
    plazo_maximo_meses = models.IntegerField(verbose_name="Plazo Máximo en Meses")
    metodo_calculo = models.CharField(max_length=20, choices=METODO_CALCULO_CHOICES, default='frances', verbose_name="Método de Cálculo")
    comision_por_desembolso = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Comisión por Desembolso (%)")

    tasa_penalidad_diaria = models.DecimalField(
        max_digits=5,
        decimal_places=4, # Allow for smaller percentages like 0.0001
        default=Decimal('0.0000'),
        verbose_name="Tasa de Penalidad Diaria (%)",
        help_text="Tasa diaria aplicada sobre el monto de la cuota vencida (ej. 0.01 para 1%)."
    )
    dias_gracia = models.IntegerField(
        default=0,
        verbose_name="Días de Gracia",
        help_text="Número de días después del vencimiento antes de aplicar penalidad."
    )
    APLICA_PENALIDAD_CHOICES = [
        ('monto_cuota', 'Monto de la Cuota'),
        ('capital_pendiente', 'Capital Pendiente de la Cuota'),
    ]
    aplica_penalidad_sobre = models.CharField(
        max_length=20,
        choices=APLICA_PENALIDAD_CHOICES,
        default='monto_cuota',
        verbose_name="Aplica Penalidad Sobre",
        help_text="Define sobre qué monto se calcula la penalidad diaria."
    )

    requiere_garantia = models.BooleanField(
        default=False,
        verbose_name="¿Requiere Garantía?",
        help_text="Marcar si este tipo de préstamo exige una garantía o requisito adicional."
    )

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'prestamos_tipo_prestamo'
        verbose_name = "Tipo de Préstamo"
        verbose_name_plural = "Tipos de Préstamos"


# ==================================================
# === MODELO PRESTAMO ===
# ==================================================
# Almacena los detalles de cada préstamo otorgado a un cliente.
class Prestamo(models.Model):
    # Define las opciones para el campo `estado`. Esto crea un menú desplegable en el admin.
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
    ]
    # Nuevas opciones para la frecuencia de pago
    FRECUENCIA_CHOICES = [
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    ]

    TIPO_AMORTIZACION_CHOICES = [
        ('saldo_insoluto', 'Saldo Insoluto'),
        ('capital_fijo', 'Capital Fijo'),
        ('interes_simple', 'Interés Simple'),
    ]

    MANEJO_GASTOS_CHOICES = [
        ('sumar_al_capital', 'Sumar al Capital'),
        ('restar_del_desembolso', 'Restar del Desembolso'),
    ]

    # `ForeignKey` crea una relación "muchos a uno" con el modelo Cliente. 
    # Un cliente puede tener muchos préstamos, pero un préstamo pertenece a un solo cliente.
    # `on_delete=models.CASCADE` significa que si se borra un cliente, todos sus préstamos se borrarán en cascada.
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="prestamos")
    
    # Clave foránea al nuevo modelo TipoPrestamo. Es opcional.
    tipo_prestamo = models.ForeignKey(TipoPrestamo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Préstamo")

    # `DecimalField` es ideal para guardar dinero, ya que evita problemas de redondeo.
    # `max_digits` es el número total de dígitos, y `decimal_places` es el número de decimales.
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto del Préstamo")
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Tasa de Interés", help_text="En porcentaje (%)")
    periodo_tasa = models.CharField(max_length=10, choices=TipoPrestamo.PERIODO_TASA_CHOICES, default='anual', verbose_name="Periodo de la Tasa")
    
    # `IntegerField` es para números enteros.
    plazo = models.IntegerField(verbose_name="Plazo", help_text="En meses")
    
    # `DateField` es para guardar solo fechas (sin hora).
    fecha_desembolso = models.DateField(verbose_name="Fecha de Desembolso")
    fecha_inicio_pago = models.DateField(verbose_name="Fecha de Inicio de Pago", null=True, blank=True)
    
    # `choices` limita los valores de este campo a las opciones definidas en `ESTADO_CHOICES`.
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente', verbose_name="Estado")
    
    # Nuevo campo para la frecuencia de pago
    frecuencia_pago = models.CharField(
        max_length=10,
        choices=FRECUENCIA_CHOICES,
        default='mensual',
        verbose_name="Frecuencia de Pago"
    )

    tipo_amortizacion = models.CharField(
        max_length=20,
        choices=TIPO_AMORTIZACION_CHOICES,
        default='saldo_insoluto',
        verbose_name="Tipo de Amortización"
    )

    manejo_gastos = models.CharField(
        max_length=30,
        choices=MANEJO_GASTOS_CHOICES,
        default='sumar_al_capital',
        verbose_name="Manejo de Gastos Adicionales"
    )

    total_gastos_asociados = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total de Gastos Asociados")
    monto_desembolsado = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto Desembolsado")

    garante = models.ForeignKey('Garante', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Garante")

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Aprobación")

    def __str__(self):
        return f"Préstamo #{self.id} - {self.cliente.nombres} {self.cliente.apellidos}"

    def registrar_pago(self, monto_pagado):
        """
        Registra un pago para este préstamo, lo distribuye entre las cuotas pendientes
        y devuelve una lista de los objetos Pago creados.
        """
        pagos_creados = []
        monto_a_distribuir = monto_pagado
        cuotas_pendientes = self.cuotas.filter(
            estado__in=['pendiente', 'pagada_parcialmente', 'vencida']
        ).order_by('numero_cuota')

        for cuota in cuotas_pendientes:
            if monto_a_distribuir <= 0:
                break

            monto_necesario = cuota.monto_total_a_pagar - cuota.total_pagado
            pago_a_cuota = min(monto_a_distribuir, monto_necesario)

            nuevo_pago = Pago.objects.create(
                cuota=cuota,
                monto_pagado=pago_a_cuota
            )
            pagos_creados.append(nuevo_pago)
            
            cuota.actualizar_estado()
            monto_a_distribuir -= pago_a_cuota

        if not self.cuotas.filter(estado__in=['pendiente', 'pagada_parcialmente', 'vencida']).exists():
            self.estado = 'pagado'
            self.save()
        
        return pagos_creados

    class Meta:
        db_table = 'prestamos_prestamo'
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        # Se añade una restricción a nivel de base de datos.
        # Esto previene que un mismo cliente pueda tener más de un préstamo
        # con el estado 'activo' al mismo tiempo.
        constraints = [
            UniqueConstraint(
                fields=['cliente'],
                condition=Q(estado='aprobado'),
                name='unique_active_loan_per_client'
            )
        ]


# ==================================================
# === MODELO CUOTA ===
# ==================================================
# Almacena el plan de pagos (amortización) de cada préstamo.
class Cuota(models.Model):
    ESTADO_CUOTA_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('vencida', 'Vencida'),
        ('pagada_parcialmente', 'Pagada Parcialmente'),
    ]

    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name="cuotas")
    numero_cuota = models.IntegerField(verbose_name="Número de Cuota")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto de la Cuota")
    capital = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Capital")
    interes = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Interés")
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Saldo Pendiente")
    estado = models.CharField(max_length=20, choices=ESTADO_CUOTA_CHOICES, default='pendiente', verbose_name="Estado")

    monto_penalidad_acumulada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Penalidad Acumulada"
    )
    fecha_ultima_penalidad_calculada = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha Última Penalidad Calculada"
    )

    def __str__(self):
        return f"Cuota {self.numero_cuota} - {self.prestamo.cliente} (Préstamo #{self.prestamo.id})"

    @property
    def total_pagado(self):
        return self.pagos.aggregate(total=models.Sum('monto_pagado'))['total'] or Decimal(0)

    @property
    def monto_total_a_pagar(self):
        """Suma el monto de la cuota y la penalidad acumulada."""
        return self.monto_cuota + self.monto_penalidad_acumulada

    def actualizar_estado(self):
        total_pagado_actual = self.total_pagado

        # AHORA SE COMPARA CON EL MONTO TOTAL (CUOTA + PENALIDAD)
        if total_pagado_actual >= self.monto_total_a_pagar:
            self.estado = 'pagada'
        elif total_pagado_actual > Decimal('0.00'):
            self.estado = 'pagada_parcialmente'
        else:
            self.estado = 'pendiente'
        self.save()

    class Meta:
        db_table = 'prestamos_cuota'
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        unique_together = ('prestamo', 'numero_cuota')
        ordering = ['prestamo', 'numero_cuota']


# ==================================================
# === MODELO PAGO ===
# ==================================================
# Almacena cada pago individual realizado para una cuota específica.
class Pago(models.Model):
    # Relación con la cuota que se está pagando.
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE, related_name="pagos")
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Pagado")
    fecha_pago = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Pago")

    def __str__(self):
        return f"Pago de {self.monto_pagado} para la cuota #{self.cuota.numero_cuota} del préstamo #{self.cuota.prestamo.id}"

    class Meta:
        db_table = 'prestamos_pago'
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

# ==================================================
# === MODELO CAPITAL ===
# ==================================================
# Almacena el capital inicial de la empresa.
class Capital(models.Model):
    monto_inicial = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Capital Inicial",
        help_text="Monto con el que la empresa inició operaciones. Solo debe existir un registro."
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Registro"
    )

    def __str__(self):
        # Formatear el monto con comas como separadores de miles y dos decimales
        return f"Capital Inicial: ${self.monto_inicial:,.2f}"

    class Meta:
        db_table = 'prestamos_capital'
        verbose_name = "Capital de la Empresa"
        verbose_name_plural = "Capital de la Empresa"


# ==================================================
# === MODELO REQUISITO ===
# ==================================================
# Almacena los requisitos o garantías asociadas a un préstamo.
class Requisito(models.Model):
    TIPO_CHOICES = [
        ('titulo_vehiculo', 'Título de Vehículo'),
        ('titulo_propiedad', 'Título de Propiedad'),
        ('garantia_solidaria', 'Garantía Solidaria'),
        ('carta_trabajo', 'Carta de Trabajo'),
        ('otro', 'Otro'),
    ]
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='requisitos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='otro', verbose_name="Tipo de Requisito")
    descripcion = models.CharField(max_length=255, help_text="Detalles del requisito (ej: Marca y placa del vehículo, No. de matrícula del inmueble, etc.)")
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Valor estimado (solo si aplica, para garantías monetarias)")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Requisito para Préstamo #{self.prestamo.id}: {self.descripcion}"

    class Meta:
        verbose_name = "Requisito"
        verbose_name_plural = "Requisitos"