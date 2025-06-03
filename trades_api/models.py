from django.db import models
# from django.utils import timezone # Not currently used as timestamp is client-provided

# This class defines what a 'Trade' looks like in our database
class Trade(models.Model):
    ticker = models.CharField(max_length=10) # e.g., "AAPL", "GOOG"
    price = models.DecimalField(max_digits=10, decimal_places=2) # For storing money values accurately
    quantity = models.IntegerField() # How many shares
    # 'side' can only be 'BUY' or 'SELL'
    side = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    timestamp = models.DateTimeField() # When the trade happened, provided by the client

    # This is how a Trade object will look if printed (e.g., in Django admin)
    def __str__(self):
        return f"{self.side} {self.quantity} {self.ticker} @ {self.price} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
