from django.contrib import admin
from .models import Transaction, Budget


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'category', 'date', 'created_at')
    list_filter = ('transaction_type', 'category', 'date', 'user')
    search_fields = ('description', 'user__username', 'category')
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'monthly_budget', 'month', 'year')
    list_filter = ('month', 'year', 'category', 'user')
    search_fields = ('user__username', 'category')
