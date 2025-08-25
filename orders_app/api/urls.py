from django.urls import path
from .views import OrdersView, OrderUpdateDeleteView

app_name = 'offers_app'
urlpatterns = [
    path('orders/', OrdersView.as_view(), name='orders'),
    path('orders/<int:pk>/', OrderUpdateDeleteView.as_view(), name='order-detail')
]