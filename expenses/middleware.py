import os
from django.core.management import call_command
from django.contrib.auth.models import User

class AutoAdminMiddleware:
    _admin_checked = False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not AutoAdminMiddleware._admin_checked:
            try:
                # Ensure database schema exists in the live container
                call_command('migrate', interactive=False)

                username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
                email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
                password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin12345!')

                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={'email': email, 'is_staff': True, 'is_superuser': True, 'is_active': True}
                )
                user.email = email
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.set_password(password)
                user.save()
                
                # Mark checked only after successful database setup
                AutoAdminMiddleware._admin_checked = True
            except Exception as e:
                print(f"AutoAdminMiddleware error: {e}")

        response = self.get_response(request)
        return response
