from django.contrib import admin
from .models import PlanCuentas, EjercicioContable, AsientoContable, DetalleAsiento

@admin.register(PlanCuentas)
class PlanCuentasAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre_cuenta', 'tipo_cuenta', 'nivel', 'activa']
    list_filter = ['tipo_cuenta', 'activa']
    search_fields = ['codigo', 'nombre_cuenta']

@admin.register(EjercicioContable)
class EjercicioContableAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_inicio', 'fecha_fin', 'estado']
    list_filter = ['estado']

class DetalleAsientoInline(admin.TabularInline):
    model = DetalleAsiento
    extra = 2

@admin.register(AsientoContable)
class AsientoContableAdmin(admin.ModelAdmin):
    list_display = ['numero_asiento', 'fecha', 'concepto', 'ejercicio', 'total_debe', 'total_haber']
    list_filter = ['ejercicio', 'tipo_asiento']
    inlines = [DetalleAsientoInline]

@admin.register(DetalleAsiento)
class DetalleAsientoAdmin(admin.ModelAdmin):
    list_display = ['asiento', 'cuenta', 'debe', 'haber']
    list_filter = ['cuenta']