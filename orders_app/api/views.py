from django.db import models
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from orders_app.models import Order
from .serializers import OrderReadSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from .permissions import IsCustomerForCreate, NotOrderingOwnOffer, IsOrderParticipant
from .permissions import IsBusinessUser

class OrdersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsCustomerForCreate, NotOrderingOwnOffer]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderReadSerializer

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOrderParticipant]
    queryset = Order.objects.select_related("customer_user", "business_user", "offer", "offer_detail")

    def get_serializer_class(self):
        # Für PATCH/PUT nur den Status-Update-Serializer verwenden
        if self.request.method in ['PUT', 'PATCH']:
            return OrderStatusUpdateSerializer
        return OrderReadSerializer
    
    def get_permissions(self):
        permissions = super().get_permissions()
        if self.request.method in ['PUT', 'PATCH']:
            permissions.append(IsBusinessUser())
        return permissions

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.business_user_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to update this order.")
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Nutzt den Status-Update-Serializer für die Validierung/Speicherung
        und gibt anschließend die komplette Order mit dem Read-Serializer zurück.
        """
        partial = kwargs.pop('partial', request.method == 'PATCH')
        instance = self.get_object()

        # Eingabe validieren & speichern (nur 'status')
        input_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        input_serializer.is_valid(raise_exception=True)
        self.perform_update(input_serializer)

        # Neu laden (wegen updated_at etc.) und volle Darstellung zurückgeben
        instance.refresh_from_db()
        output_serializer = OrderReadSerializer(instance)
        return Response(output_serializer.data)