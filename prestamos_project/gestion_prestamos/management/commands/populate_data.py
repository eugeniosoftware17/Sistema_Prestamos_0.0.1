
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from gestion_prestamos.models import (Cliente, Cuota, Pago, Prestamo,
                                      TipoPrestamo)


class Command(BaseCommand):
    help = "Populate the database with realistic sample data spanning the last 2 years."

    def handle(self, *args, **options):
        self.stdout.write("Starting data population process...")

        # Inicializar Faker
        fake = Faker('es_ES')  # Usar localización en español

        # --- 1. Limpiar datos existentes ---
        self.stdout.write("Cleaning old data...")
        Pago.objects.all().delete()
        Cuota.objects.all().delete()
        Prestamo.objects.all().delete()
        Cliente.objects.all().delete()
        TipoPrestamo.objects.all().delete()

        # --- 2. Crear Tipos de Préstamo ---
        self.stdout.write("Creating loan types...")
        tipo_personal = TipoPrestamo.objects.create(
            nombre="Préstamo Personal",
            tasa_interes_predeterminada=Decimal("22.5"),
            periodo_tasa='anual',
            monto_minimo=Decimal("500"),
            monto_maximo=Decimal("15000"),
            plazo_minimo_meses=6,
            plazo_maximo_meses=48,
            tasa_penalidad_diaria=Decimal("0.001"), # 0.1% diario
            dias_gracia=5
        )

        tipo_vehiculo = TipoPrestamo.objects.create(
            nombre="Préstamo de Vehículo",
            tasa_interes_predeterminada=Decimal("18.0"),
            periodo_tasa='anual',
            monto_minimo=Decimal("5000"),
            monto_maximo=Decimal("40000"),
            plazo_minimo_meses=12,
            plazo_maximo_meses=72,
            requiere_garantia=True,
            tasa_penalidad_diaria=Decimal("0.001"),
            dias_gracia=3
        )

        # --- 3. Crear Clientes ---
        self.stdout.write("Creating clients...")
        clientes = []
        for _ in range(50):
            cliente = Cliente.objects.create(
                nombres=fake.first_name(),
                apellidos=fake.last_name(),
                tipo_documento='cedula',
                numero_documento=fake.unique.numerify(text='###-#######-#'),
                direccion=fake.address(),
                telefono=fake.phone_number(),
                email=fake.unique.email(),
                fecha_nacimiento=fake.date_of_birth(minimum_age=21, maximum_age=70),
                ingresos_mensuales=Decimal(random.uniform(500, 4000))
            )
            clientes.append(cliente)

        # --- 4. Crear Préstamos, Cuotas y Pagos ---
        self.stdout.write("Creating loans, installments, and payments...")
        today = timezone.now().date()

        for cliente in clientes:
            # Crear entre 1 y 3 préstamos por cliente
            num_prestamos = random.randint(1, 3)
            for i in range(num_prestamos):
                # El último préstamo puede estar activo, los anteriores estarán pagados
                is_last_loan = (i == num_prestamos - 1)
                
                tipo_prestamo = random.choice([tipo_personal, tipo_vehiculo])
                
                # Fechas aleatorias en los últimos 2 años
                dias_atras = random.randint(1, 365 * 2)
                fecha_desembolso = today - timedelta(days=dias_atras)
                
                monto = Decimal(random.randrange(int(tipo_prestamo.monto_minimo), int(tipo_prestamo.monto_maximo), 100))
                plazo = random.randint(tipo_prestamo.plazo_minimo_meses, tipo_prestamo.plazo_maximo_meses)

                # Determinar estado
                if not is_last_loan or random.random() < 0.8: # 80% de los préstamos antiguos/actuales están pagados
                    estado_prestamo = 'pagado'
                else:
                    estado_prestamo = 'aprobado'

                prestamo = Prestamo.objects.create(
                    cliente=cliente,
                    tipo_prestamo=tipo_prestamo,
                    monto=monto,
                    tasa_interes=tipo_prestamo.tasa_interes_predeterminada,
                    periodo_tasa=tipo_prestamo.periodo_tasa,
                    plazo=plazo,
                    fecha_desembolso=fecha_desembolso,
                    fecha_inicio_pago=fecha_desembolso + timedelta(days=30),
                    estado=estado_prestamo,
                    frecuencia_pago='mensual'
                )

                # --- 5. Generar Cuotas (Amortización Francesa Simplificada) ---
                tasa_mensual = (prestamo.tasa_interes / Decimal(100)) / Decimal(12)
                if tasa_mensual > 0:
                    monto_cuota = (monto * tasa_mensual) / (1 - (1 + tasa_mensual) ** -plazo)
                else:
                    monto_cuota = monto / plazo
                
                monto_cuota = monto_cuota.quantize(Decimal('0.01'))

                saldo_pendiente = monto
                for n in range(1, plazo + 1):
                    interes = (saldo_pendiente * tasa_mensual).quantize(Decimal('0.01'))
                    capital = (monto_cuota - interes).quantize(Decimal('0.01'))
                    saldo_pendiente -= capital
                    fecha_vencimiento = prestamo.fecha_inicio_pago + timedelta(days=(n-1)*30)

                    estado_cuota = 'pendiente'
                    if estado_prestamo == 'pagado':
                        estado_cuota = 'pagada'
                    elif fecha_vencimiento < today:
                        estado_cuota = 'vencida'

                    cuota = Cuota.objects.create(
                        prestamo=prestamo,
                        numero_cuota=n,
                        fecha_vencimiento=fecha_vencimiento,
                        monto_cuota=monto_cuota,
                        capital=capital,
                        interes=interes,
                        saldo_pendiente=max(saldo_pendiente, Decimal(0)),
                        estado=estado_cuota
                    )

                    # --- 6. Generar Pagos ---
                    if cuota.estado == 'pagada':
                        Pago.objects.create(
                            cuota=cuota,
                            monto_pagado=cuota.monto_cuota,
                            # La fecha de pago se establece automáticamente
                        )
        
        self.stdout.write(self.style.SUCCESS("Successfully populated the database."))
