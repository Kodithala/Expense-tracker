/**
 * Expense Tracker Application JavaScript Utility Module
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Sidebar Navigation Toggle
    const mobileToggleBtn = document.getElementById('mobileToggleBtn');
    const sidebar = document.getElementById('sidebar');

    if (mobileToggleBtn && sidebar) {
        mobileToggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function (e) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !mobileToggleBtn.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            }
        });
    }

    // 2. Dynamic Category Options depending on Transaction Type (Income vs Expense)
    const txTypeSelect = document.getElementById('id_transaction_type');
    const categorySelect = document.getElementById('id_category');

    if (txTypeSelect && categorySelect) {
        const expenseCategories = [
            'Food', 'Travel', 'Shopping', 'Bills',
            'Entertainment', 'Health', 'Education', 'Others'
        ];

        const incomeCategories = [
            'Salary', 'Business', 'Freelance',
            'Investment', 'Gift', 'Other Income'
        ];

        function updateCategoryOptions() {
            const selectedType = txTypeSelect.value;
            const currentSelectedCategory = categorySelect.value;
            categorySelect.innerHTML = '';

            let categoriesToDisplay = selectedType === 'INCOME' ? incomeCategories : expenseCategories;

            categoriesToDisplay.forEach(function (cat) {
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                if (cat === currentSelectedCategory) {
                    option.selected = true;
                }
                categorySelect.appendChild(option);
            });
        }

        txTypeSelect.addEventListener('change', updateCategoryOptions);

        // Run once on load if category isn't pre-filled by model instance
        if (!categorySelect.value) {
            updateCategoryOptions();
        }
    }

    // 3. Auto-dismiss Alert Messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease-out';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // 4. Progress Bars Initialization
    const progressFills = document.querySelectorAll('[data-pct]');
    progressFills.forEach(function (el) {
        const pct = parseFloat(el.getAttribute('data-pct')) || 0;
        el.style.width = Math.min(Math.max(pct, 0), 100) + '%';
    });
});
