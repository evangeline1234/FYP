from django.db import models

class CarparkRates(models.Model):
    id = models.AutoField(primary_key=True)
    carparkcode = models.CharField(max_length=255)
    carparkname = models.CharField(max_length=255)
    vehcat = models.CharField(max_length=255)
    starttime = models.TimeField()
    endtime = models.TimeField()
    weekdayrate = models.DecimalField(max_digits=10, decimal_places=2)
    weekdaymin = models.IntegerField()
    satdayrate = models.DecimalField(max_digits=10, decimal_places=2)
    satdaymin = models.IntegerField()
    sunphrate = models.DecimalField(max_digits=10, decimal_places=2)
    sunphmin = models.IntegerField()
    parkingsystem = models.CharField(max_length=255)
    parkcapacity = models.IntegerField()
    geometries = models.JSONField()

    def __str__(self):
        return self.carparkcode

    class Meta:
        db_table = 'carpark_rates'
    

   