from django.db import models

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    cash = models.DecimalField(max_digits=15, decimal_places=2, default=1000.00)

    class Meta:
        unique_together = ['symbol', 'date']

    def __str__(self):
        return f"{self.symbol} - {self.date}"
