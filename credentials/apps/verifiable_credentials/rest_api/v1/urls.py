"""verifiable_credentials API v1 URLs."""
from rest_framework import routers

from credentials.apps.verifiable_credentials.rest_api.v1 import views


router = routers.DefaultRouter()
router.register(r"program_credentials", views.ProgramCredentialsViewSet, basename="program_credentials")

urlpatterns = []

urlpatterns += router.urls
