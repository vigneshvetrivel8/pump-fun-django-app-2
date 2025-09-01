from django.db import models

# Create your models here.
# pumplistener/models.py

class Token(models.Model):
    timestamp = models.DateTimeField()
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    mint_address = models.CharField(max_length=100, unique=True)
    sol_amount = models.FloatField()
    creator_address = models.CharField(max_length=100)

    # ADD THIS LINE
    pump_fun_link = models.CharField(max_length=200, default='')

    def __str__(self):
        return f"{self.name} ({self.symbol})"