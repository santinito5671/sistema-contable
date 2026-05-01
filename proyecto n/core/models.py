from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class PlanCuentas(models.Model):
    TIPOS_CUENTA = [
        ('A', 'Activo'),
        ('P', 'Pasivo'),
        ('C', 'Capital'),
        ('I', 'Ingreso'),
        ('G', 'Gasto'),
    ]
 
    codigo = models.CharField(max_length=20, unique=True)
    nombre_cuenta = models.CharField(max_length=200)
    tipo_cuenta = models.CharField(max_length=1, choices=TIPOS_CUENTA)
    nivel = models.IntegerField()
    cuenta_padre = models.CharField(max_length=20, null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre_cuenta}"

class EjercicioContable(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, default='ABIERTO')
    
    def __str__(self):
        return self.nombre

class AsientoContable(models.Model):
    TIPOS_ASIENTO = [
        ('RG', 'Regular'),
        ('AJ', 'Ajuste'),
    ]
    
    numero_asiento = models.IntegerField()
    fecha = models.DateField()
    concepto = models.TextField()
    ejercicio = models.ForeignKey(EjercicioContable, on_delete=models.PROTECT)
    tipo_asiento = models.CharField(max_length=2, choices=TIPOS_ASIENTO)
    total_debe = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_haber = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Asiento #{self.numero_asiento} - {self.fecha}"

class DetalleAsiento(models.Model):
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name='detalles')
    cuenta = models.ForeignKey(PlanCuentas, on_delete=models.PROTECT)
    debe = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    haber = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    descripcion = models.CharField(max_length=300, blank=True)
    
    def __str__(self):
        return f"{self.cuenta.codigo} - D: {self.debe} H: {self.haber}"

@receiver(pre_save, sender=AsientoContable)
def validar_partida_doble(sender, instance, **kwargs):
    if instance.total_debe != instance.total_haber:
        raise ValidationError('El asiento no está balanceado')