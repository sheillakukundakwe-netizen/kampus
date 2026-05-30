import os
import sys

from werkzeug.wrappers import Response

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lostfound.settings')
import django
django.setup()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


def handler(request):
    return Response.from_app(application, request.environ)
