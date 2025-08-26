from django.db import models
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from orders_app.models import Order
from .serializers import OrderSerializer

class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )

class OrderUpdateDeleteView(APIView):
    pass