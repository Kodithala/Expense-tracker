from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
import datetime
from .models import Transaction, Budget


class ExpenseTrackerTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='Password123!')
        self.user2 = User.objects.create_user(username='testuser2', password='Password123!')
        self.client1 = Client()
        self.client1.login(username='testuser1', password='Password123!')

        # Create sample transactions for user1
        self.tx1 = Transaction.objects.create(
            user=self.user1,
            transaction_type='INCOME',
            amount=Decimal('50000.00'),
            category='Salary',
            description='Monthly Salary',
            date=datetime.date.today()
        )
        self.tx2 = Transaction.objects.create(
            user=self.user1,
            transaction_type='EXPENSE',
            amount=Decimal('4500.00'),
            category='Food',
            description='Groceries',
            date=datetime.date.today()
        )

    def test_dashboard_calculations(self):
        response = self.client1.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_income'], Decimal('50000.00'))
        self.assertEqual(response.context['total_expenses'], Decimal('4500.00'))
        self.assertEqual(response.context['current_balance'], Decimal('45500.00'))

    def test_add_transaction(self):
        response = self.client1.post(reverse('add_transaction'), {
            'transaction_type': 'EXPENSE',
            'amount': '1200.00',
            'category': 'Travel',
            'description': 'Taxi fare',
            'date': datetime.date.today().strftime('%Y-%m-%d')
        })
        self.assertRedirects(response, reverse('transactions'))
        self.assertTrue(Transaction.objects.filter(description='Taxi fare', user=self.user1).exists())

    def test_data_isolation_edit(self):
        # Create transaction belonging to user2
        tx_user2 = Transaction.objects.create(
            user=self.user2,
            transaction_type='EXPENSE',
            amount=Decimal('1000.00'),
            category='Shopping',
            description='Secret expense',
            date=datetime.date.today()
        )

        # User1 attempts to access/edit User2's transaction -> should return 404
        edit_url = reverse('edit_transaction', kwargs={'pk': tx_user2.pk})
        response = self.client1.get(edit_url)
        self.assertEqual(response.status_code, 404)

    def test_budget_creation_and_alert(self):
        today = datetime.date.today()
        budget = Budget.objects.create(
            user=self.user1,
            category='Food',
            monthly_budget=Decimal('5000.00'),
            month=today.month,
            year=today.year
        )
        response = self.client1.get(reverse('budget'))
        self.assertEqual(response.status_code, 200)
        card = response.context['budget_cards'][0]
        self.assertEqual(card['spent'], Decimal('4500.00'))
        self.assertEqual(card['raw_percentage'], 90.0)
        self.assertEqual(card['warning_level'], 'critical')
