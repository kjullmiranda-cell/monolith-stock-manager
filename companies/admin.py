
from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "nuit",
        "email",
        "phone",
        "is_active",
        "created_at",
    )

    search_fields = ("name", "nuit", "email")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("created_at",)
    exclude = ("slug",)

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
