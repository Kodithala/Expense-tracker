# Expense Tracker Web Application

A full-stack **Expense Tracker Web Application** built using **Python, Django, Django ORM, SQLite, custom CSS, and Chart.js**.

The application enables users to manage personal finances, track income and expenses across customizable categories, set category monthly budgets with automated threshold warnings, and visualize spending habits through interactive financial analytics dashboards.

---

## Key Features

- **User Authentication**: Secure registration, login, and logout with data isolation ensuring users only access their own transactions.
- **Transaction Management**: Add, edit, delete, and view Income and Expenses with amount, category, description, and date.
- **Dynamic Dashboard**:
  - Live statistics cards calculating Total Income, Total Expenses, and Net Current Balance (`Balance = Income - Expenses`).
  - Interactive Chart.js visualizations (Monthly Trend Bar Chart and Expense Breakdown Doughnut Chart).
  - Recent transactions overview table.
- **Transaction History & Filtering**:
  - Filter transactions by keyword search, transaction type (Income/Expense), category, and date range.
  - Pagination (10 transactions per page).
- **Budget Management**:
  - Set category-wise monthly budgets.
  - Track spent vs remaining budget with dynamic progress bars.
  - Automated threshold alerts at **80%**, **90%**, and **100% (Exceeded)** spending limits.
- **Financial Analytics & Reports**:
  - Monthly financial summary metrics.
  - 12-Month income vs expense trend comparison.
  - Category percentage allocation tables.

---

## Technology Stack

- **Backend**: Python 3, Django 5, Django ORM, SQLite
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6)
- **Data Visualization**: Chart.js (CDN)
- **Iconography & Typography**: FontAwesome 6, Google Fonts (Plus Jakarta Sans)

---

## Getting Started & Setup Instructions

Follow these step-by-step instructions to run the application on your local machine:

### 1. Prerequisites

Ensure you have Python 3.10+ installed on your system.

### 2. Create a Virtual Environment

Open your terminal or PowerShell in the project root directory (`expense-tracker`):

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**On Windows (PowerShell / Command Prompt):**
```powershell
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

Install Django and required Python packages:

```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations

Apply database migrations to setup the SQLite database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin User)

Create an administrative superuser to access Django Admin:

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

### 7. Start the Development Server

Launch the Django local development server:

```bash
python manage.py runserver
```

Once started, open your web browser and navigate to:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Project Structure

```
.
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── expenses/
│   ├── migrations/
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── templates/
│   ├── base.html
│   ├── authentication/
│   │   ├── login.html
│   │   └── register.html
│   └── expenses/
│       ├── dashboard.html
│       ├── add_transaction.html
│       ├── edit_transaction.html
│       ├── transaction_list.html
│       ├── delete_transaction.html
│       ├── budget.html
│       └── reports.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

---

## Running Automated Unit Tests

To run the automated Django test suite:

```bash
python manage.py test expenses
```
