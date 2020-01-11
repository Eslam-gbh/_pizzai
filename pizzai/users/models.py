import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city_id = models.ForeignKey('City', on_delete=models.PROTECT, null=True)
    address = models.TextField(null=True)
    contact_phone = models.CharField(max_length=15, null=True)
    email = models.EmailField(max_length=255, unique=True)
    confirmation_code = models.CharField(max_length=255, null=True)
    time_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class City(models.Model):
    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"

    city_name = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=12)

    def __str__(self):
        return self.city_name
