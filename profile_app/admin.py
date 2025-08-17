from django.contrib import admin
from .models import UserProfile

admin.site.site_header = "Profiles Administration"
admin.site.site_title = "Profiles" 
@admin.register(UserProfile)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at')
    search_fields = ('first_name', 'last_name', 'location', 'tel', 'email')
    list_filter = ('location', 'type')
    ordering = ('id',)

    verbose_name = 'Profile'
    verbose_name_plural = 'Profiles'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')