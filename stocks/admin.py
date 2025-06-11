from django.contrib import admin
from .models import Portfolio, holding, Transaction,Strategy

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'initial_funds', 'current_funds', 'invested_amount', 'total_value', 'profit_loss_percent')
    readonly_fields = ('total_value', 'profit_loss_percent')

@admin.register(holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'quantity', 'avg_buy_price', 'current_price', 'market_value', 'unrealized_pnl')
    readonly_fields = ('market_value', 'unrealized_pnl')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'action', 'quantity', 'price', 'total_value', 'date')
    readonly_fields = ('total_value',)

@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_active', 'created_at')
