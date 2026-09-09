from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

TRANSACTION_TYPE_CHOICES = [
    ('INCOME', 'Income'),
    ('EXPENSE', 'Expense'),
]

EXPENSE_CATEGORY_CHOICES = [
    ('Food', 'Food'),
    ('Travel', 'Travel'),
    ('Shopping', 'Shopping'),
    ('Bills', 'Bills'),
    ('Entertainment', 'Entertainment'),
    ('Health', 'Health'),
    ('Education', 'Education'),
    ('Others', 'Others'),
]

INCOME_CATEGORY_CHOICES = [
    ('Salary', 'Salary'),
    ('Business', 'Business'),
    ('Freelance', 'Freelance'),
    ('Investment', 'Investment'),
    ('Gift', 'Gift'),
    ('Other Income', 'Other Income'),
]

ALL_CATEGORY_CHOICES = EXPENSE_CATEGORY_CHOICES + INCOME_CATEGORY_CHOICES


class Transaction(models.Model):
    """
    Model representing a financial transaction (Income or Expense).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        default='EXPENSE'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.CharField(max_length=50, choices=ALL_CATEGORY_CHOICES)
    description = models.CharField(max_length=255, blank=True, help_text="Optional description")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} | {self.transaction_type} | ₹{self.amount} ({self.category})"


class Budget(models.Model):
    """
    Model representing category-wise monthly spending budgets set by users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORY_CHOICES)
    monthly_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    month = models.PositiveIntegerField(help_text="1 to 12")
    year = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')
        ordering = ['-year', '-month', 'category']

    def __str__(self):
        return f"{self.user.username} | {self.category} Budget ({self.month}/{self.year}): ₹{self.monthly_budget}"
