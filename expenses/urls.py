from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('transactions/', views.transaction_list_view, name='transactions'),
    path('transactions/add/', views.add_transaction_view, name='add_transaction'),
    path('transactions/<int:pk>/edit/', views.edit_transaction_view, name='edit_transaction'),
    path('transactions/<int:pk>/delete/', views.delete_transaction_view, name='delete_transaction'),
    path('budget/', views.budget_list_view, name='budget'),
    path('reports/', views.reports_view, name='reports'),
]
