import os
from django.contrib.auth.models import User

class AutoAdminMiddleware:
    _admin_checked = False

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not AutoAdminMiddleware._admin_checked:
            try:
                username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
                email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
                password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin12345!')

                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': email, 'is_staff': True, 'is_superuser': True, 'is_active': True}
                )
                user.email = email
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.set_password(password)
                user.save()
                AutoAdminMiddleware._admin_checked = True
            except Exception as e:
                print(f"AutoAdminMiddleware initialization note: {e}")

        response = self.get_response(request)
        return response
