"""verifiable_credentials API v1 URLs."""
from django.urls import re_path
from rest_framework import routers

from credentials.apps.verifiable_credentials.rest_api.v1 import views


router = routers.DefaultRouter()
router.register(r"program_credentials", views.ProgramCredentialsViewSet, basename="program_credentials")

urlpatterns = [
    re_path(r"^qrcode/$", views.QRCodeView.as_view(), name="qrcode"),
    re_path(r"^deeplink/$", views.DeeplinkView.as_view(), name="deeplink"),
    re_path(
        r"^credentials/issue/(?P<issuance_uuid>[a-zA-Z0-9]+)/$",
        views.IssueCredentialView.as_view(),
        name="credentials-issue",
    ),
]

urlpatterns += router.urls
