""" API v2 URLs. """
from rest_framework.routers import DefaultRouter

from credentials.apps.api.v2 import views


router = DefaultRouter()  # pylint: disable=invalid-name
# URL can not have hyphen as it is not currently supported by slumber
# as mentioned https://github.com/samgiles/slumber/issues/44
router.register(r'program_credentials', views.ProgramsCredentialsViewSet, base_name='programcredential')
urlpatterns = router.urls
