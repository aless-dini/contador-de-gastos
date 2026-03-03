from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Gasto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    precio = models.FloatField()
    categoria = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)
    fecha = models.DateField()
    
    def __str__(self):
        return f"{self.categoria} - ${self.precio}"

class Presupuesto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.FloatField()
    mes = models.IntegerField()
    año = models.IntegerField()

    class Meta:
        unique_together = ['user', 'mes', 'año']  # un presupuesto por mes por usuario

    def __str__(self):
        return f"{self.user} - {self.mes}/{self.año}"