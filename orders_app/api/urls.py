from django.urls import path

from .views import OrdersView, OrderDetailView, OrderCountView, OrderCompletetdCountView

app_name = 'offers_app'
urlpatterns = [
    path('orders/', OrdersView.as_view(), name='orders'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', OrderCompletetdCountView.as_view(), name='order-count')
]
