from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import AsientoContable, PlanCuentas, EjercicioContable, DetalleAsiento
from django.contrib import messages
from django.db import transaction

def index(request):
    """Página principal del sistema"""
    # Obtener estadísticas básicas
    total_asientos = AsientoContable.objects.count()
    total_cuentas = PlanCuentas.objects.filter(activa=True).count()
    
    # Últimos asientos
    ultimos_asientos = AsientoContable.objects.all().order_by('-fecha')[:5]
    
    context = {
        'total_asientos': total_asientos,
        'total_cuentas': total_cuentas,
        'ultimos_asientos': ultimos_asientos,
    }
    return render(request, 'core/index.html', context)

def lista_asientos(request):
    """Lista todos los asientos contables"""
    asientos = AsientoContable.objects.all().order_by('-fecha', '-numero_asiento')
    
    context = {
        'asientos': asientos,
    }
    return render(request, 'core/lista_asientos.html', context)

def crear_asiento(request):
    """Vista para crear un nuevo asiento contable"""
    cuentas = PlanCuentas.objects.filter(activa=True)
    ejercicios = EjercicioContable.objects.filter(estado='ABIERTO')
    
    print(f"Cuentas disponibles: {cuentas.count()}")  # DEBUG
    print(f"Ejercicios disponibles: {ejercicios.count()}")  # DEBUG
    
    if request.method == 'POST':
        print("POST recibido:", request.POST)  # DEBUG
        try:
            with transaction.atomic():
                # Obtener el próximo número de asiento
                ultimo_asiento = AsientoContable.objects.order_by('-numero_asiento').first()
                proximo_numero = ultimo_asiento.numero_asiento + 1 if ultimo_asiento else 1
                
                # Crear el asiento
                asiento = AsientoContable(
                    numero_asiento=proximo_numero,
                    fecha=request.POST.get('fecha'),
                    concepto=request.POST.get('concepto'),
                    ejercicio_id=request.POST.get('ejercicio'),
                    tipo_asiento='RG',
                    total_debe=0,
                    total_haber=0
                )
                asiento.full_clean()  # Validar el modelo
                asiento.save()
                
                # Procesar las 2 líneas del formulario
                total_debe = 0
                total_haber = 0
                
                for i in range(1, 3):  # Procesar línea 1 y 2
                    cuenta_id = request.POST.get(f'cuenta_{i}')
                    debe_str = request.POST.get(f'debe_{i}', '0')
                    haber_str = request.POST.get(f'haber_{i}', '0')
                    
                    if cuenta_id and (debe_str or haber_str):
                        try:
                            debe = float(debe_str) if debe_str else 0.0
                            haber = float(haber_str) if haber_str else 0.0
                            
                            if debe > 0 or haber > 0:
                                detalle = DetalleAsiento(
                                    asiento=asiento,
                                    cuenta_id=cuenta_id,
                                    debe=debe,
                                    haber=haber,
                                    descripcion=request.POST.get('concepto', '')[:300]
                                )
                                detalle.save()
                                
                                total_debe += debe
                                total_haber += haber
                                
                        except ValueError:
                            messages.error(request, f'Error en los montos de la línea {i}')
                            return redirect('/asientos/crear/')
                
                # Validar partida doble
                if total_debe != total_haber:
                    asiento.delete()  # Eliminar asiento incompleto
                    messages.error(request, f'El asiento no está balanceado. Debe: ${total_debe:.2f}, Haber: ${total_haber:.2f}')
                    return redirect('/asientos/crear/')
                
                # Actualizar totales del asiento
                asiento.total_debe = total_debe
                asiento.total_haber = total_haber
                asiento.save()
                
                messages.success(request, f'Asiento #{proximo_numero} creado exitosamente')
                return redirect('/asientos/')
                
        except Exception as e:
            messages.error(request, f'Error al crear el asiento: {str(e)}')
    
    context = {
        'cuentas': cuentas,
        'ejercicios': ejercicios,
    }
    return render(request, 'core/crear_asiento.html', context)
import csv
from django.http import HttpResponse
from datetime import datetime

def exportar_asientos_csv(request):
    """Exporta todos los asientos contables a CSV"""
    # Crear respuesta HTTP con archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="asientos_contables_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    
    # Crear writer CSV
    writer = csv.writer(response)
    
    # Escribir headers (basado en tu lógica JS)
    writer.writerow([
        'Número Asiento',
        'Fecha', 
        'Concepto',
        'Ejercicio',
        'Tipo Asiento',
        'Total Debe',
        'Total Haber',
        'Cuenta Código',
        'Cuenta Nombre', 
        'Debe',
        'Haber',
        'Descripción'
    ])
    
    # Obtener todos los asientos con sus detalles
    asientos = AsientoContable.objects.all().prefetch_related('detalles__cuenta')
    
    # Escribir filas (similar a tu lógica de mapeo en JS)
    for asiento in asientos:
        for detalle in asiento.detalles.all():
            writer.writerow([
                asiento.numero_asiento,
                asiento.fecha.strftime('%Y-%m-%d'),
                asiento.concepto,
                asiento.ejercicio.nombre,
                asiento.tipo_asiento,
                f"{asiento.total_debe:.2f}",
                f"{asiento.total_haber:.2f}",
                detalle.cuenta.codigo,
                detalle.cuenta.nombre_cuenta,
                f"{detalle.debe:.2f}",
                f"{detalle.haber:.2f}",
                detalle.descripcion or ''
            ])
    
    return response
def exportar_balance_csv(request):
    """Exporta el balance de comprobación a CSV"""
    from django.db.models import Sum
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="balance_comprobacion_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Código', 'Nombre Cuenta', 'Total Debe', 'Total Haber', 'Saldo Deudor', 'Saldo Acreedor'])
    
    # Reutilizar la lógica del balance
    cuentas_con_movimientos = DetalleAsiento.objects.values(
        'cuenta_id', 
        'cuenta__codigo', 
        'cuenta__nombre_cuenta'
    ).annotate(
        total_debe=Sum('debe'),
        total_haber=Sum('haber')
    ).order_by('cuenta__codigo')
    
    for cuenta in cuentas_con_movimientos:
        saldo_deudor = max(0, (cuenta['total_debe'] or 0) - (cuenta['total_haber'] or 0))
        saldo_acreedor = max(0, (cuenta['total_haber'] or 0) - (cuenta['total_debe'] or 0))
        
        writer.writerow([
            cuenta['cuenta__codigo'],
            cuenta['cuenta__nombre_cuenta'],
            f"{(cuenta['total_debe'] or 0):.2f}",
            f"{(cuenta['total_haber'] or 0):.2f}",
            f"{saldo_deudor:.2f}",
            f"{saldo_acreedor:.2f}"
        ])
    
    return response
def exportar_plantilla_csv(request):
    """Exporta una plantilla CSV para importar asientos"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plantilla_importacion_asientos.csv"'
    
    writer = csv.writer(response)
    
    # Headers de la plantilla
    writer.writerow(['fecha', 'concepto', 'cuenta_codigo', 'debe', 'haber', 'descripcion'])
    
    # Ejemplos de datos
    writer.writerow(['2024-01-15', 'Venta de productos', '1.1.1.01', '1000.00', '0.00', 'Venta al contado'])
    writer.writerow(['2024-01-15', 'Venta de productos', '4.1.1', '0.00', '1000.00', 'Ingreso por venta'])
    writer.writerow(['2024-01-16', 'Pago de servicios', '5.2.2', '500.00', '0.00', 'Pago luz'])
    writer.writerow(['2024-01-16', 'Pago de servicios', '1.1.1.02', '0.00', '500.00', 'Pago desde banco'])
    
    return response
def importar_asientos_csv(request):
    """Importa asientos contables desde archivo CSV"""
    cuentas = PlanCuentas.objects.filter(activa=True)
    ejercicios = EjercicioContable.objects.filter(estado='ABIERTO')
    
    if request.method == 'POST':
        archivo_csv = request.FILES.get('archivo_csv')
        ejercicio_id = request.POST.get('ejercicio_id')
        
        if not archivo_csv or not ejercicio_id:
            messages.error(request, 'Debe seleccionar un archivo y un ejercicio contable')
        else:
            try:
                # Leer archivo CSV
                decoded_file = archivo_csv.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                
                asientos_creados = 0
                errores = []
                
                with transaction.atomic():
                    # Procesar cada fila del CSV
                    for numero_fila, fila in enumerate(reader, 2):  # Empieza en 2 por el header
                        try:
                            # Validar campos requeridos
                            fecha = fila.get('fecha', '').strip()
                            concepto = fila.get('concepto', '').strip()
                            cuenta_codigo = fila.get('cuenta_codigo', '').strip()
                            debe_str = fila.get('debe', '0').strip()
                            haber_str = fila.get('haber', '0').strip()
                            
                            if not all([fecha, concepto, cuenta_codigo]):
                                errores.append(f"Fila {numero_fila}: Campos requeridos faltantes")
                                continue
                            
                            # Buscar cuenta por código
                            try:
                                cuenta = PlanCuentas.objects.get(codigo=cuenta_codigo, activa=True)
                            except PlanCuentas.DoesNotExist:
                                errores.append(f"Fila {numero_fila}: Cuenta '{cuenta_codigo}' no existe")
                                continue
                            
                            # Convertir montos
                            try:
                                debe = float(debe_str) if debe_str else 0.0
                                haber = float(haber_str) if haber_str else 0.0
                            except ValueError:
                                errores.append(f"Fila {numero_fila}: Montos inválidos (debe: {debe_str}, haber: {haber_str})")
                                continue
                            
                            # Para simplificar, creamos un asiento por cada línea
                            # En una versión mejorada, agruparíamos por concepto/fecha
                            ultimo_asiento = AsientoContable.objects.order_by('-numero_asiento').first()
                            proximo_numero = ultimo_asiento.numero_asiento + 1 if ultimo_asiento else 1
                            
                            asiento = AsientoContable(
                                numero_asiento=proximo_numero,
                                fecha=fecha,
                                concepto=concepto,
                                ejercicio_id=ejercicio_id,
                                tipo_asiento='RG',
                                total_debe=debe,
                                total_haber=haber
                            )
                            asiento.save()
                            
                            # Crear detalle
                            DetalleAsiento.objects.create(
                                asiento=asiento,
                                cuenta=cuenta,
                                debe=debe,
                                haber=haber,
                                descripcion=fila.get('descripcion', '')[:300]
                            )
                            
                            asientos_creados += 1
                            
                        except Exception as e:
                            errores.append(f"Fila {numero_fila}: {str(e)}")
                            continue
                
                # Mostrar resultados
                if asientos_creados > 0:
                    messages.success(request, f'Se importaron {asientos_creados} asientos correctamente')
                if errores:
                    messages.warning(request, f'Se encontraron {len(errores)} errores durante la importación')
                    # Guardar errores en sesión para mostrarlos detalladamente
                    request.session['import_errors'] = errores[:10]  # Mostrar solo primeros 10 errores
                
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
    
    # Mostrar errores detallados si existen
    errores_detallados = request.session.pop('import_errors', [])
    
    context = {
        'cuentas': cuentas,
        'ejercicios': ejercicios,
        'errores_detallados': errores_detallados,
    }
    return render(request, 'core/importar_asientos.html', context)
def balance_comprobacion(request):
    """Genera el balance de comprobación"""
    from django.db.models import Sum
    from decimal import Decimal
    
    # Obtener todas las cuentas con movimientos
    cuentas_con_movimientos = DetalleAsiento.objects.values(
        'cuenta_id', 
        'cuenta__codigo', 
        'cuenta__nombre_cuenta'
    ).annotate(
        total_debe=Sum('debe'),
        total_haber=Sum('haber')
    ).order_by('cuenta__codigo')
    
    # Calcular saldos
    balance = []
    for cuenta in cuentas_con_movimientos:
        saldo_deudor = max(0, (cuenta['total_debe'] or 0) - (cuenta['total_haber'] or 0))
        saldo_acreedor = max(0, (cuenta['total_haber'] or 0) - (cuenta['total_debe'] or 0))
        
        balance.append({
            'codigo': cuenta['cuenta__codigo'],
            'nombre': cuenta['cuenta__nombre_cuenta'],
            'total_debe': cuenta['total_debe'] or 0,
            'total_haber': cuenta['total_haber'] or 0,
            'saldo_deudor': saldo_deudor,
            'saldo_acreedor': saldo_acreedor,
        })
    
    # Calcular totales generales
    total_debe = sum(item['total_debe'] for item in balance)
    total_haber = sum(item['total_haber'] for item in balance)
    total_saldo_deudor = sum(item['saldo_deudor'] for item in balance)
    total_saldo_acreedor = sum(item['saldo_acreedor'] for item in balance)
    
    context = {
        'balance': balance,
        'total_debe': total_debe,
        'total_haber': total_haber,
        'total_saldo_deudor': total_saldo_deudor,
        'total_saldo_acreedor': total_saldo_acreedor,
    }
    return render(request, 'core/balance_comprobacion.html', context)
def estado_resultados(request):
    """Genera el Estado de Resultados (Pérdidas y Ganancias)"""
    from django.db.models import Sum, Q
    from decimal import Decimal
    
    # Obtener ingresos (cuentas tipo 'I' - 4.x.x)
    ingresos = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='I'
    ).aggregate(
        total=Sum('haber') - Sum('debe')
    )['total'] or Decimal('0')
    
    # Obtener gastos (cuentas tipo 'G' - 5.x.x)
    gastos = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='G'
    ).aggregate(
        total=Sum('debe') - Sum('haber')
    )['total'] or Decimal('0')
    
    # Calcular utilidad
    utilidad_neta = ingresos - gastos
    
    # Detalle por categoría
    categorias_ingresos = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='I'
    ).values(
        'cuenta__codigo', 'cuenta__nombre_cuenta'
    ).annotate(
        total=(Sum('haber') - Sum('debe'))
    ).order_by('cuenta__codigo')
    
    categorias_gastos = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='G'
    ).values(
        'cuenta__codigo', 'cuenta__nombre_cuenta'
    ).annotate(
        total=(Sum('debe') - Sum('haber'))
    ).order_by('cuenta__codigo')
    
    context = {
        'ingresos': ingresos,
        'gastos': gastos,
        'utilidad_neta': utilidad_neta,
        'categorias_ingresos': categorias_ingresos,
        'categorias_gastos': categorias_gastos,
        'periodo': 'Enero 2024 - Diciembre 2024'  
    }
    return render(request, 'core/estado_resultados.html', context)
def balance_general(request):
    """Genera el Balance General (Activo = Pasivo + Patrimonio)"""
    from django.db.models import Sum, Q
    from decimal import Decimal
    
    # Activos (cuentas tipo 'A')
    activos = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='A'
    ).aggregate(
        total=Sum('debe') - Sum('haber')
    )['total'] or Decimal('0')
    
    # Pasivos (cuentas tipo 'P') 
    pasivos = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='P'
    ).aggregate(
        total=Sum('haber') - Sum('debe')
    )['total'] or Decimal('0')
    
    # Patrimonio (cuentas tipo 'C')
    patrimonio = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='C'
    ).aggregate(
        total=Sum('haber') - Sum('debe')
    )['total'] or Decimal('0')
    
    # Detalle de activos
    detalle_activos = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='A'
    ).values(
        'cuenta__codigo', 'cuenta__nombre_cuenta'
    ).annotate(
        total=(Sum('debe') - Sum('haber'))
    ).filter(total__gt=0).order_by('cuenta__codigo')
    
    # Detalle de pasivos
    detalle_pasivos = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='P'
    ).values(
        'cuenta__codigo', 'cuenta__nombre_cuenta'
    ).annotate(
        total=(Sum('haber') - Sum('debe'))
    ).filter(total__gt=0).order_by('cuenta__codigo')
    
    # Detalle de patrimonio
    detalle_patrimonio = DetalleAsiento.objects.filter(
        cuenta__tipo_cuenta='C'
    ).values(
        'cuenta__codigo', 'cuenta__nombre_cuenta'
    ).annotate(
        total=(Sum('haber') - Sum('debe'))
    ).filter(total__gt=0).order_by('cuenta__codigo')
    
    # Verificar ecuación fundamental: Activo = Pasivo + Patrimonio
    total_pasivo_patrimonio = pasivos + patrimonio
    balanceado = activos == total_pasivo_patrimonio
    diferencia = activos - total_pasivo_patrimonio
    
    context = {
        'activos': activos,
        'pasivos': pasivos,
        'patrimonio': patrimonio,
        'total_pasivo_patrimonio': total_pasivo_patrimonio,
        'balanceado': balanceado,
        'diferencia': diferencia,
        'detalle_activos': detalle_activos,
        'detalle_pasivos': detalle_pasivos,
        'detalle_patrimonio': detalle_patrimonio,
        'periodo': 'Al 31 de Diciembre 2024'
    }
    return render(request, 'core/balance_general.html', context)
def libro_mayor(request):
    """Muestra el libro mayor para una cuenta específica"""
    from django.db.models import Sum
    from decimal import Decimal
    
    cuentas = PlanCuentas.objects.filter(activa=True)
    cuenta_seleccionada = None
    movimientos = []
    saldo_actual = Decimal('0')
    total_debe = Decimal('0')
    total_haber = Decimal('0')
    
    if request.method == 'GET' and 'cuenta_id' in request.GET:
        cuenta_id = request.GET.get('cuenta_id')
        
        try:
            cuenta_seleccionada = PlanCuentas.objects.get(id=cuenta_id)
            
            # Obtener todos los movimientos de la cuenta
            movimientos = DetalleAsiento.objects.filter(
                cuenta=cuenta_seleccionada
            ).select_related('asiento', 'asiento__ejercicio').order_by('asiento__fecha', 'asiento__numero_asiento')
            
            # Calcular totales
            total_debe = sum(movimiento.debe for movimiento in movimientos)
            total_haber = sum(movimiento.haber for movimiento in movimientos)
            
            # Calcular saldo acumulado
            saldo_acumulado = Decimal('0')
            for movimiento in movimientos:
                movimiento.saldo_parcial = saldo_acumulado
                if cuenta_seleccionada.tipo_cuenta in ['A', 'G']:  # Activos y Gastos: +debe, -haber
                    saldo_acumulado += movimiento.debe - movimiento.haber
                else:  # Pasivos, Patrimonio, Ingresos: -debe, +haber
                    saldo_acumulado += movimiento.haber - movimiento.debe
                movimiento.saldo_final = saldo_acumulado
            
            saldo_actual = saldo_acumulado
            
        except PlanCuentas.DoesNotExist:
            messages.error(request, 'La cuenta seleccionada no existe')
    
    context = {
        'cuentas': cuentas,
        'cuenta_seleccionada': cuenta_seleccionada,
        'movimientos': movimientos,
        'saldo_actual': saldo_actual,
        'total_debe': total_debe,
        'total_haber': total_haber,
    }
    return render(request, 'core/libro_mayor.html', context)
def ver_asiento(request, asiento_id):
    """Muestra los detalles completos de un asiento contable"""
    try:
        asiento = AsientoContable.objects.select_related('ejercicio').prefetch_related('detalles__cuenta').get(id=asiento_id)
        
        context = {
            'asiento': asiento,
            'detalles': asiento.detalles.all(),
        }
        return render(request, 'core/ver_asiento.html', context)
        
    except AsientoContable.DoesNotExist:
        messages.error(request, 'El asiento solicitado no existe')
        return redirect('/asientos/')