from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'type', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('type', 'is_active', 'is_staff')
    ordering = ('id',)

    verbose_name = 'User'
    verbose_name_plural = 'Users'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')