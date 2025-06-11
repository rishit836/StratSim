from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    initial_funds = models.DecimalField(max_digits=15, decimal_places=2, default=100000)
    current_funds = models.DecimalField(max_digits=15, decimal_places=2, default=100000)
    invested_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    previous_return_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    def total_value(self):
        return self.current_funds + self.invested_amount

    def profit_loss_percent(self):
        if self.initial_funds == 0:
            return 0
        return ((self.total_value() - self.initial_funds) / self.initial_funds) * 100
    
    def profit_loss_percent(self):
        if self.initial_funds == 0:
            return 0
        return ((self.total_value() - self.initial_funds) / self.initial_funds) * 100
    
    def update_return_history(self):
        current_return = self.profit_loss_percent()
        change = current_return - self.previous_return_percent
        self.previous_return_percent = current_return
        self.save()
        return change

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
    

class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"
