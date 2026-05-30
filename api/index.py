import os
import sys
from pathlib import Path

from werkzeug.wrappers import Response

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lostfound.settings')
import django
django.setup()

from django.conf import settings
from django.core.asgi import get_asgi_application
from django.core.management import call_command

application = get_asgi_application()


def ensure_database():
    default_db = settings.DATABASES['default']
    if default_db['ENGINE'] == 'django.db.backends.sqlite3':
        db_path = Path(default_db['NAME'])
        if not db_path.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)
            call_command('migrate', interactive=False, run_syncdb=True)


ensure_database()


def handler(request):
    return Response.from_app(application, request.environ)
