import datetime
import uuid

import factory
from django.core.files.base import ContentFile
from factory.django import ImageField

from credentials.apps.core.tests.factories import SiteFactory
from credentials.apps.credentials import constants, models


PASSWORD = "dummy-password"


def create_image(extension: str) -> ContentFile:
    return ContentFile(
        ImageField()._make_data({"width": 1289, "height": 720}),  # pylint: disable=protected-access
        f"example.{extension}",
    )


class AbstractCertificateFactory(factory.django.DjangoModelFactory):
    site = factory.SubFactory(SiteFactory)


class CourseCertificateFactory(AbstractCertificateFactory):
    class Meta:
        model = models.CourseCertificate

    course_id = factory.Sequence(lambda o: "course-%d" % o)
    certificate_type = constants.CertificateType.HONOR
    is_active = True
    certificate_available_date = None
    course_run = None
    title = factory.Faker("word")


class ProgramCertificateFactory(AbstractCertificateFactory):
    class Meta:
        model = models.ProgramCertificate

    is_active = True
    program_uuid = factory.LazyFunction(uuid.uuid4)


class UserCredentialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UserCredential

    credential = factory.SubFactory(ProgramCertificateFactory)
    username = factory.Sequence(lambda o: "robot%d" % o)
    status = models.UserCredential.AWARDED
    download_url = factory.Faker("url")
    uuid = factory.LazyFunction(uuid.uuid4)


class UserCredentialAttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UserCredentialAttribute

    user_credential = factory.SubFactory(UserCredentialFactory)
    name = factory.Sequence(lambda o: "name-%d" % o)
    value = factory.Sequence(lambda o: "value-%d" % o)


class UserCredentialDateOverrideFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UserCredentialDateOverride

    date = datetime.date(2021, 5, 11)


class SignatoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Signatory

    name = factory.Faker("name")
    title = factory.Faker("job")
    image = factory.LazyAttribute(lambda _: create_image("png"))
