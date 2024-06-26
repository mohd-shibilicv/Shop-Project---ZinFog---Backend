import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop_project_zinfog.settings")

application = get_wsgi_application()
