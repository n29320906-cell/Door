from django.contrib import admin
from .models import StoreProfile


@admin.register(StoreProfile)
class StoreProfileAdmin(admin.ModelAdmin):
    list_display = ("store_name", "manager_name", "phone", "city", "user")
    search_fields = ("store_name", "manager_name", "user__username", "user__email")
    list_select_related = ("user",)
