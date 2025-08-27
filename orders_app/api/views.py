from django.db import models
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from orders_app.models import Order
from .serializers import OrderSerializer
from .permissions import IsCustomerForCreate, NotOrderingOwnOffer, IsOrderParticipant

class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerForCreate, NotOrderingOwnOffer]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderParticipant]
    queryset = Order.objects.select_related("customer_user", "business_user", "offer", "offer_detail")