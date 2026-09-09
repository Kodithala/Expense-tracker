from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
import datetime
from .models import (
    Transaction, Budget,
    TRANSACTION_TYPE_CHOICES,
    EXPENSE_CATEGORY_CHOICES,
    INCOME_CATEGORY_CHOICES,
    ALL_CATEGORY_CHOICES
)


class UserRegistrationForm(forms.ModelForm):
    """
    Form for new user registration with password confirmation.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }),
        min_length=6,
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
        }

    def clean_username(self):
        cleaned_data = self.cleaned_data or {}
        username = cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        cleaned_data = self.cleaned_data or {}
        email = cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with that email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean() or {}
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter.")
        return cleaned_data


class TransactionForm(forms.ModelForm):
    """
    Form to add or edit financial transactions.
    """
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'category', 'description', 'date']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_transaction_type'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Grocery shopping, Monthly salary, Client invoice'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default date to today if creating new record
        if not self.instance.pk and not self.initial.get('date'):
            self.initial['date'] = datetime.date.today().strftime('%Y-%m-%d')

    def clean_amount(self):
        cleaned_data = self.cleaned_data or {}
        amount = cleaned_data.get('amount')
        if amount is None or amount <= Decimal('0'):
            raise ValidationError("Amount must be greater than zero.")
        return amount

    def clean_date(self):
        cleaned_data = self.cleaned_data or {}
        date = cleaned_data.get('date')
        if not date:
            raise ValidationError("Transaction date cannot be empty.")
        return date

    def clean(self):
        cleaned_data = super().clean() or {}
        tx_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')

        if not tx_type:
            self.add_error('transaction_type', "Transaction type is required.")

        if not category:
            self.add_error('category', "Category is required.")

        return cleaned_data


class BudgetForm(forms.ModelForm):
    """
    Form to set category monthly budget.
    """
    class Meta:
        model = Budget
        fields = ['category', 'monthly_budget', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'monthly_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 5000.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'month': forms.Select(
                choices=[(m, datetime.date(2000, m, 1).strftime('%B')) for m in range(1, 13)],
                attrs={'class': 'form-select'}
            ),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2000',
                'max': '2100'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = datetime.date.today()
        if not self.instance.pk:
            if not self.initial.get('month'):
                self.initial['month'] = today.month
            if not self.initial.get('year'):
                self.initial['year'] = today.year

    def clean_monthly_budget(self):
        cleaned_data = self.cleaned_data or {}
        budget = cleaned_data.get('monthly_budget')
        if budget is None or budget <= Decimal('0'):
            raise ValidationError("Budget value must be a positive number greater than zero.")
        return budget

    def clean_month(self):
        cleaned_data = self.cleaned_data or {}
        month = cleaned_data.get('month')
        if month is None or month < 1 or month > 12:
            raise ValidationError("Invalid month selected.")
        return month


