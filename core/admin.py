from django.contrib import admin
from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['slug', 'name', 'is_active', 'created_on', 'updated_on']
    readonly_fields = ['slug', 'created_on', 'updated_on']

    def has_delete_permission(self, request, obj=None):
        return False
