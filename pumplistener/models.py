from django.db import models

class Token(models.Model):
    timestamp = models.DateTimeField()
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    mint_address = models.CharField(max_length=100, unique=True)
    sol_amount = models.FloatField()
    creator_address = models.CharField(max_length=100)
    pump_fun_link = models.CharField(max_length=200, default='')
    is_from_watchlist = models.BooleanField(default=False)

    # --- NEW FIELDS TO TRACK TRADE STATE ---
    is_sold = models.BooleanField(default=False)
    buy_timestamp = models.DateTimeField(null=True, blank=True)
    sell_timestamp = models.DateTimeField(null=True, blank=True)
    
    initial_market_cap = models.FloatField(null=True, blank=True)
    current_market_cap = models.FloatField(null=True, blank=True)
    highest_market_cap = models.FloatField(null=True, blank=True)
    current_holder_count = models.IntegerField(null=True, blank=True)
    peak_holder_count = models.IntegerField(null=True, blank=True)
    sell_market_cap = models.FloatField(null=True, blank=True)
    # --- END OF NEW FIELDS ---
        # --- ADD THIS LINE ---
    buy_transaction_sig = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
class TokenDataPoint(models.Model):
    token = models.ForeignKey(Token, related_name='data_points', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return f"Data for {self.token.symbol} at {self.timestamp}"