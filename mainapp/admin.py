from django.contrib import admin
from .models import growth

# Register your models here.
@admin.register(growth)
class GrowthAdmin(admin.ModelAdmin):
    list_display = ('user','fund_history')