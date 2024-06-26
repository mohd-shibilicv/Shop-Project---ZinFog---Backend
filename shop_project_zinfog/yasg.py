from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Shop ZinFog API",
        default_version="v1",
        description="API documentation for the Shop project for ZinFog",
        terms_of_service="https://www.zinfog.com/policies/terms/",
        contact=openapi.Contact(email="contact@zinfog.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)
