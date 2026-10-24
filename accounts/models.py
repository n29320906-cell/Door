from django.db import models
from django.conf import settings


class StoreProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_profile"
    )

    store_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Название магазина"
    )
    manager_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="ФИО менеджера"
    )
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=200, blank=True)
    house = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.store_name or self.user.username

