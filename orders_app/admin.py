from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'customer_user', 'business_user', 'revisions','delivery_time_in_days','price','features', 'offer_type', 'status', 'created_at', 'updated_at')

    