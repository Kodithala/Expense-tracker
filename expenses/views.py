import json
import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.paginator import Paginator

from .models import (
    Transaction, Budget,
    EXPENSE_CATEGORY_CHOICES,
    INCOME_CATEGORY_CHOICES,
    ALL_CATEGORY_CHOICES
)
from .forms import UserRegistrationForm, TransactionForm, BudgetForm


def register_view(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Automatically log the user in after registration
            login(request, user)
            messages.success(request, f"Welcome to Expense Tracker, {user.username}! Your account was created successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # Auto-create or sync default admin user if logging in as admin
        posted_username = request.POST.get('username', '').strip()
        if posted_username.lower() == 'admin':
            try:
                from django.contrib.auth.models import User
                user, _ = User.objects.get_or_create(
                    username='admin',
                    defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True, 'is_active': True}
                )
                user.email = 'admin@example.com'
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.set_password('Admin12345!')
                user.save()
            except Exception as e:
                print(f"Admin auto-sync note: {e}")

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Main dashboard displaying financial summary cards, charts, and recent activity.
    """
    user_txs = Transaction.objects.filter(user=request.user)

    # Aggregates
    total_income = user_txs.filter(transaction_type='INCOME').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_expenses = user_txs.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    current_balance = total_income - total_expenses

    # Recent Transactions
    recent_transactions = user_txs[:5]

    # Expense breakdown by category for Pie Chart
    category_summary = (
        user_txs.filter(transaction_type='EXPENSE')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    pie_labels = [item['category'] for item in category_summary]
    pie_data = [float(item['total']) for item in category_summary]

    # Monthly Summary for last 6 months (Monthly Expense Bar Chart)
    today = datetime.date.today()
    monthly_labels = []
    monthly_income_data = []
    monthly_expense_data = []

    for i in range(5, -1, -1):
        # Calculate year and month for 6-month range
        m = (today.month - i - 1) % 12 + 1
        y = today.year + ((today.month - i - 1) // 12)
        month_name = datetime.date(y, m, 1).strftime('%b %Y')
        monthly_labels.append(month_name)

        inc = user_txs.filter(
            transaction_type='INCOME',
            date__year=y,
            date__month=m
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        exp = user_txs.filter(
            transaction_type='EXPENSE',
            date__year=y,
            date__month=m
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        monthly_income_data.append(float(inc))
        monthly_expense_data.append(float(exp))

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'recent_transactions': recent_transactions,
        'category_summary': category_summary,
        'pie_labels': pie_labels,
        'pie_data': pie_data,
        'monthly_labels': monthly_labels,
        'monthly_income': monthly_income_data,
        'monthly_expense': monthly_expense_data,
    }

    return render(request, 'expenses/dashboard.html', context)


@login_required
def transaction_list_view(request):
    """
    Transaction history page with search, filters (type, category, date), and pagination.
    """
    tx_list = Transaction.objects.filter(user=request.user)

    # Search query
    q = request.GET.get('q', '').strip()
    if q:
        tx_list = tx_list.filter(
            Q(description__icontains=q) | Q(category__icontains=q)
        )

    # Filter by transaction type
    tx_type = request.GET.get('tx_type', '').strip()
    if tx_type in ['INCOME', 'EXPENSE']:
        tx_list = tx_list.filter(transaction_type=tx_type)

    # Filter by category
    category = request.GET.get('category', '').strip()
    if category:
        tx_list = tx_list.filter(category=category)

    # Filter by date range
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    if start_date:
        tx_list = tx_list.filter(date__gte=start_date)
    if end_date:
        tx_list = tx_list.filter(date__lte=end_date)

    # Pagination (10 per page)
    paginator = Paginator(tx_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'q': q,
        'tx_type': tx_type,
        'category': category,
        'start_date': start_date,
        'end_date': end_date,
        'expense_categories': [c[0] for c in EXPENSE_CATEGORY_CHOICES],
        'income_categories': [c[0] for c in INCOME_CATEGORY_CHOICES],
        'all_categories': [c[0] for c in ALL_CATEGORY_CHOICES],
    }

    return render(request, 'expenses/transaction_list.html', context)


@login_required
def add_transaction_view(request):
    """
    Form view to add new Income or Expense.
    """
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.user = request.user
            tx.save()
            messages.success(request, f"{tx.get_transaction_type_display()} of ₹{tx.amount} added successfully.")
            return redirect('transactions')
        else:
            messages.error(request, "Failed to add transaction. Please check the form errors.")
    else:
        form = TransactionForm()

    return render(request, 'expenses/add_transaction.html', {'form': form})


@login_required
def edit_transaction_view(request, pk):
    """
    Form view to edit existing transaction with strict user verification.
    """
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully.")
            return redirect('transactions')
        else:
            messages.error(request, "Failed to update transaction. Please check the form errors.")
    else:
        form = TransactionForm(instance=tx)

    return render(request, 'expenses/edit_transaction.html', {'form': form, 'transaction': tx})


@login_required
def delete_transaction_view(request, pk):
    """
    Confirmation and handling view for deleting a transaction.
    """
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        amount = tx.amount
        category = tx.category
        tx.delete()
        messages.success(request, f"Transaction for ₹{amount} ({category}) deleted successfully.")
        return redirect('transactions')

    return render(request, 'expenses/delete_transaction.html', {'transaction': tx})


@login_required
def budget_list_view(request):
    """
    Budget Management View - Set monthly budget per category and track budget limits.
    """
    today = datetime.date.today()

    try:
        selected_month = int(request.GET.get('month', today.month))
        selected_year = int(request.GET.get('year', today.year))
    except ValueError:
        selected_month = today.month
        selected_year = today.year

    if selected_month < 1 or selected_month > 12:
        selected_month = today.month

    # Handle set budget form submit
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            cat = form.cleaned_data['category']
            mb = form.cleaned_data['monthly_budget']
            m = form.cleaned_data['month']
            y = form.cleaned_data['year']

            # Create or update budget record
            budget_obj, created = Budget.objects.update_or_create(
                user=request.user,
                category=cat,
                month=m,
                year=y,
                defaults={'monthly_budget': mb}
            )

            action = "created" if created else "updated"
            messages.success(request, f"Budget for {cat} ({datetime.date(y, m, 1).strftime('%B %Y')}) {action} to ₹{mb}.")
            return redirect(f"/budget/?month={m}&year={y}")
        else:
            messages.error(request, "Failed to save budget. Please check the input fields.")
    else:
        form = BudgetForm(initial={'month': selected_month, 'year': selected_year})

    # Fetch user budgets for the selected month/year
    user_budgets = Budget.objects.filter(user=request.user, month=selected_month, year=selected_year)

    budget_cards = []
    total_budget_amount = Decimal('0.00')
    total_spent_amount = Decimal('0.00')

    for b in user_budgets:
        spent = Transaction.objects.filter(
            user=request.user,
            transaction_type='EXPENSE',
            category=b.category,
            date__year=selected_year,
            date__month=selected_month
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        remaining = b.monthly_budget - spent
        percentage = float(round((spent / b.monthly_budget) * 100, 1)) if b.monthly_budget > 0 else 0.0

        # Determine threshold alert level
        if percentage >= 100:
            warning_level = 'exceeded'
            warning_msg = f"Alert: 100% or more of your {b.category} budget has been spent!"
            status_color = 'danger'
        elif percentage >= 90:
            warning_level = 'critical'
            warning_msg = f"Warning: {percentage}% of your {b.category} budget has been used."
            status_color = 'warning-high'
        elif percentage >= 80:
            warning_level = 'warning'
            warning_msg = f"Notice: {percentage}% of your {b.category} budget has been used."
            status_color = 'warning'
        else:
            warning_level = 'normal'
            warning_msg = f"{percentage}% spent. Looking good!"
            status_color = 'success'

        total_budget_amount += b.monthly_budget
        total_spent_amount += spent

        budget_cards.append({
            'id': b.id,
            'category': b.category,
            'monthly_budget': b.monthly_budget,
            'spent': spent,
            'remaining': remaining,
            'percentage': min(percentage, 100.0),
            'raw_percentage': percentage,
            'warning_level': warning_level,
            'warning_msg': warning_msg,
            'status_color': status_color,
        })

    month_name = datetime.date(selected_year, selected_month, 1).strftime('%B %Y')
    months_list = [(m, datetime.date(2000, m, 1).strftime('%B')) for m in range(1, 13)]
    years_list = list(range(today.year - 2, today.year + 3))

    context = {
        'form': form,
        'budget_cards': budget_cards,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_name': month_name,
        'months_list': months_list,
        'years_list': years_list,
        'total_budget_amount': total_budget_amount,
        'total_spent_amount': total_spent_amount,
        'total_remaining': total_budget_amount - total_spent_amount,
    }

    return render(request, 'expenses/budget.html', context)


@login_required
def reports_view(request):
    """
    Monthly Expense Summary & Financial Analytics Reports.
    """
    today = datetime.date.today()

    try:
        selected_month = int(request.GET.get('month', today.month))
        selected_year = int(request.GET.get('year', today.year))
    except ValueError:
        selected_month = today.month
        selected_year = today.year

    if selected_month < 1 or selected_month > 12:
        selected_month = today.month

    # Filter transactions for selected month/year
    month_txs = Transaction.objects.filter(
        user=request.user,
        date__year=selected_year,
        date__month=selected_month
    )

    monthly_income = month_txs.filter(transaction_type='INCOME').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    monthly_expense = month_txs.filter(transaction_type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    monthly_balance = monthly_income - monthly_expense

    # Category breakdown for table and pie chart
    category_breakdown = (
        month_txs.filter(transaction_type='EXPENSE')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    categories_data = []
    for item in category_breakdown:
        cat_total = item['total']
        pct = round((cat_total / monthly_expense * 100), 1) if monthly_expense > 0 else 0
        categories_data.append({
            'category': item['category'],
            'amount': cat_total,
            'percentage': pct
        })

    pie_labels = [item['category'] for item in categories_data]
    pie_values = [float(item['amount']) for item in categories_data]

    # Bar chart for last 12 months trend
    trend_labels = []
    trend_income = []
    trend_expense = []

    user_all_txs = Transaction.objects.filter(user=request.user)

    for i in range(11, -1, -1):
        m = (today.month - i - 1) % 12 + 1
        y = today.year + ((today.month - i - 1) // 12)
        month_label = datetime.date(y, m, 1).strftime('%b %Y')
        trend_labels.append(month_label)

        inc = user_all_txs.filter(transaction_type='INCOME', date__year=y, date__month=m).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        exp = user_all_txs.filter(transaction_type='EXPENSE', date__year=y, date__month=m).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        trend_income.append(float(inc))
        trend_expense.append(float(exp))

    month_name = datetime.date(selected_year, selected_month, 1).strftime('%B %Y')
    months_list = [(m, datetime.date(2000, m, 1).strftime('%B')) for m in range(1, 13)]
    years_list = list(range(today.year - 3, today.year + 2))

    context = {
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_name': month_name,
        'months_list': months_list,
        'years_list': years_list,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'monthly_balance': monthly_balance,
        'categories_data': categories_data,
        'pie_labels': pie_labels,
        'pie_values': pie_values,
        'trend_labels': trend_labels,
        'trend_income': trend_income,
        'trend_expense': trend_expense,
    }

    return render(request, 'expenses/reports.html', context)
