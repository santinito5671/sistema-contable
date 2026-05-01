import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'contabilidad.settings')
django.setup()

from core.models import PlanCuentas, EjercicioContable

def crear_plan_cuentas():
    """Crea el plan de cuentas básico para una Sociedad Anónima"""
    
    cuentas = [
        # ACTIVO
        {'codigo': '1', 'nombre_cuenta': 'ACTIVO', 'tipo_cuenta': 'A', 'nivel': 1},
        {'codigo': '1.1', 'nombre_cuenta': 'ACTIVO CORRIENTE', 'tipo_cuenta': 'A', 'nivel': 2, 'cuenta_padre': '1'},
        {'codigo': '1.1.1', 'nombre_cuenta': 'CAJA Y BANCOS', 'tipo_cuenta': 'A', 'nivel': 3, 'cuenta_padre': '1.1'},
        {'codigo': '1.1.1.01', 'nombre_cuenta': 'CAJA', 'tipo_cuenta': 'A', 'nivel': 4, 'cuenta_padre': '1.1.1'},
        {'codigo': '1.1.1.02', 'nombre_cuenta': 'BANCOS', 'tipo_cuenta': 'A', 'nivel': 4, 'cuenta_padre': '1.1.1'},
        {'codigo': '1.1.2', 'nombre_cuenta': 'INVERSIONES TEMPORARIAS', 'tipo_cuenta': 'A', 'nivel': 3, 'cuenta_padre': '1.1'},
        {'codigo': '1.1.3', 'nombre_cuenta': 'CUENTAS POR COBRAR', 'tipo_cuenta': 'A', 'nivel': 3, 'cuenta_padre': '1.1'},
        {'codigo': '1.1.3.01', 'nombre_cuenta': 'CLIENTES', 'tipo_cuenta': 'A', 'nivel': 4, 'cuenta_padre': '1.1.3'},
        
        # PASIVO
        {'codigo': '2', 'nombre_cuenta': 'PASIVO', 'tipo_cuenta': 'P', 'nivel': 1},
        {'codigo': '2.1', 'nombre_cuenta': 'PASIVO CORRIENTE', 'tipo_cuenta': 'P', 'nivel': 2, 'cuenta_padre': '2'},
        {'codigo': '2.1.1', 'nombre_cuenta': 'CUENTAS POR PAGAR', 'tipo_cuenta': 'P', 'nivel': 3, 'cuenta_padre': '2.1'},
        {'codigo': '2.1.1.01', 'nombre_cuenta': 'PROVEEDORES', 'tipo_cuenta': 'P', 'nivel': 4, 'cuenta_padre': '2.1.1'},
        {'codigo': '2.1.2', 'nombre_cuenta': 'IMPUESTOS POR PAGAR', 'tipo_cuenta': 'P', 'nivel': 3, 'cuenta_padre': '2.1'},
        
        # CAPITAL
        {'codigo': '3', 'nombre_cuenta': 'CAPITAL', 'tipo_cuenta': 'C', 'nivel': 1},
        {'codigo': '3.1', 'nombre_cuenta': 'CAPITAL SOCIAL', 'tipo_cuenta': 'C', 'nivel': 2, 'cuenta_padre': '3'},
        {'codigo': '3.2', 'nombre_cuenta': 'RESULTADOS ACUMULADOS', 'tipo_cuenta': 'C', 'nivel': 2, 'cuenta_padre': '3'},
        
        # INGRESOS
        {'codigo': '4', 'nombre_cuenta': 'INGRESOS', 'tipo_cuenta': 'I', 'nivel': 1},
        {'codigo': '4.1', 'nombre_cuenta': 'INGRESOS POR VENTAS', 'tipo_cuenta': 'I', 'nivel': 2, 'cuenta_padre': '4'},
        {'codigo': '4.1.1', 'nombre_cuenta': 'VENTAS DE PRODUCTOS', 'tipo_cuenta': 'I', 'nivel': 3, 'cuenta_padre': '4.1'},
        
        # GASTOS
        {'codigo': '5', 'nombre_cuenta': 'GASTOS', 'tipo_cuenta': 'G', 'nivel': 1},
        {'codigo': '5.1', 'nombre_cuenta': 'GASTOS DE VENTAS', 'tipo_cuenta': 'G', 'nivel': 2, 'cuenta_padre': '5'},
        {'codigo': '5.2', 'nombre_cuenta': 'GASTOS ADMINISTRATIVOS', 'tipo_cuenta': 'G', 'nivel': 2, 'cuenta_padre': '5'},
        {'codigo': '5.2.1', 'nombre_cuenta': 'SUELDOS Y SALARIOS', 'tipo_cuenta': 'G', 'nivel': 3, 'cuenta_padre': '5.2'},
        {'codigo': '5.2.2', 'nombre_cuenta': 'ALQUILERES', 'tipo_cuenta': 'G', 'nivel': 3, 'cuenta_padre': '5.2'},
    ]
    
    for cuenta_data in cuentas:
        cuenta, created = PlanCuentas.objects.get_or_create(
            codigo=cuenta_data['codigo'],
            defaults=cuenta_data
        )
        if created:
            print(f" Creada cuenta: {cuenta.codigo} - {cuenta.nombre_cuenta}")
        else:
            print(f"ℹ Ya existe: {cuenta.codigo} - {cuenta.nombre_cuenta}")

def crear_ejercicio_actual():
    """Crea el ejercicio contable actual"""
    from datetime import date
    
    ejercicio, created = EjercicioContable.objects.get_or_create(
        nombre='Ejercicio 2024',
        defaults={
            'fecha_inicio': date(2024, 1, 1),
            'fecha_fin': date(2024, 12, 31),
            'estado': 'ABIERTO'
        }
    )
    
    if created:
        print(f" Creado ejercicio: {ejercicio.nombre}")
    else:
        print(f" Ya existe ejercicio: {ejercicio.nombre}")

if __name__ == '__main__':
    print(" agregando plan de cuentas...")
    crear_plan_cuentas()
    crear_ejercicio_actual()
    print(" ¡Datos iniciales creados exitosamente!")