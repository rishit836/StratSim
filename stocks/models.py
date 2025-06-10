from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    initial_funds = models.DecimalField(max_digits=15, decimal_places=2, default=100000)
    current_funds = models.DecimalField(max_digits=15, decimal_places=2, default=100000)
    invested_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def total_value(self):
        return self.current_funds + self.invested_amount

    def profit_loss_percent(self):
        if self.initial_funds == 0:
            return 0
        return ((self.total_value() - self.initial_funds) / self.initial_funds) * 100

    def __str__(self):
        return f"{self.user.username}'s Portfolio"

class holding(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField()
    avg_buy_price = models.DecimalField(max_digits=10,decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    
    def market_value(self):
        return self.quantity * self.current_price

    def unrealized_pnl(self):
        return (self.current_price - self.avg_buy_price) * self.quantity

    def __str__(self):
        return f"{self.ticker} - {self.user.username}"
    

class Transaction(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    ACTIONS = [(BUY, 'Buy'), (SELL, 'Sell')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    action = models.CharField(max_length=4, choices=ACTIONS)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def total_value(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.action} {self.quantity} of {self.ticker} @ {self.price} by {self.user.username}"
