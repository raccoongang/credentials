"""
Verifiable Credentials API v1 URLs.
"""
from django.urls import path
from rest_framework import routers

from credentials.apps.verifiable_credentials.rest_api.v1 import views


router = routers.DefaultRouter()
router.register(r"program_credentials", views.ProgramCredentialsViewSet, basename="program_credentials")

urlpatterns = [
    path(r"credentials/init/", views.InitIssuanceView.as_view(), name="credentials-init"),
    path(
        r"credentials/issue/<uuid:issuance_line_uuid>/",
        views.IssueCredentialView.as_view(),
        name="credentials-issue",
    ),
]

urlpatterns += router.urls
