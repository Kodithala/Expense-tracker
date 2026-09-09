"""
WSGI config for config project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Run database migrations and superuser setup on WSGI app startup (for Render runtime persistence)
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    call_command('create_admin_user')
except Exception as e:
    print(f"WSGI startup initialization: {e}")

