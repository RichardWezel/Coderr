from django.contrib import admin
from reviews_app.models import Review

admin.site.site_header = "Review Administration"
admin.site.site_title = "Reviews" 
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at')
    search_fields = ()
    list_filter = ('business_user', 'reviewer', 'rating', 'created_at', 'updated_at')
    ordering = ('id',)

    verbose_name = 'Review'
    verbose_name_plural = 'Reviews'

    def get_queryset(self, request):
        return super().get_queryset(request)