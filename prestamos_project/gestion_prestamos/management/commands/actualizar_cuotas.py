from django.core.management.base import BaseCommand
from django.utils import timezone
from gestion_prestamos.models import Cuota, Prestamo
from gestion_prestamos.utils import calcular_penalidad_cuota
from decimal import Decimal

class Command(BaseCommand):
    help = 'Actualiza el estado y las penalidades de las cuotas vencidas.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Iniciando la actualización de cuotas vencidas ---'))
        
        hoy = timezone.localdate()
        
        # Seleccionar cuotas pendientes o parcialmente pagadas cuya fecha de vencimiento ya pasó.
        cuotas_vencidas = Cuota.objects.filter(
            estado__in=['pendiente', 'pagada_parcialmente'],
            fecha_vencimiento__lt=hoy
        ).select_related('prestamo__tipo_prestamo') # Optimizar la consulta

        if not cuotas_vencidas.exists():
            self.stdout.write(self.style.SUCCESS('No se encontraron cuotas vencidas para actualizar.'))
            return

        cuotas_actualizadas_count = 0
        prestamos_afectados = set()

        for cuota in cuotas_vencidas:
            # 1. Actualizar el estado a 'vencida' si es 'pendiente'
            if cuota.estado == 'pendiente':
                cuota.estado = 'vencida'
                cuota.save() # Guardar el cambio de estado
            
            # 2. Calcular la penalidad
            # La función calcular_penalidad_cuota ya guarda la cuota si hay cambios.
            calcular_penalidad_cuota(cuota)

            cuotas_actualizadas_count += 1
            prestamos_afectados.add(cuota.prestamo.id)

            self.stdout.write(f'  - Cuota #{cuota.numero_cuota} del Préstamo #{cuota.prestamo.id} actualizada. Penalidad acumulada: ${cuota.monto_penalidad_acumulada:,.2f}')

        # 3. (Opcional) Actualizar el estado de los préstamos que ahora están vencidos.
        # Un préstamo se considera vencido si tiene al menos una cuota vencida.
        Prestamo.objects.filter(id__in=prestamos_afectados, estado='aprobado').update(estado='vencido')

        self.stdout.write(self.style.SUCCESS(f'--- Proceso completado. ---'))
        self.stdout.write(self.style.SUCCESS(f'Total de cuotas actualizadas: {cuotas_actualizadas_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total de préstamos afectados y marcados como "Vencido": {len(prestamos_afectados)}'))
