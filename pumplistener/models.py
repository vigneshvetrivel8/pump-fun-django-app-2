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

    # ADD THIS NEW FIELD
    is_from_watchlist = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
    
# --- ADD THIS NEW MODEL ---
class TokenDataPoint(models.Model):
    token = models.ForeignKey(Token, related_name='data_points', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    # We'll store the collected API data as a JSON object
    data = models.JSONField()

    def __str__(self):
        return f"Data for {self.token.symbol} at {self.timestamp}"