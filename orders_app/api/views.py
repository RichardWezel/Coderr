from django.db import models

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response

from auth_app.models import CustomUser
from orders_app.models import Order
from .serializers import OrderReadSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer, OrderCountSerializer
from .permissions import IsCustomerForCreate, NotOrderingOwnOffer, IsOrderParticipant, IsBusinessUser, IsStaffOrAdminForDelete

class OrdersView(generics.ListCreateAPIView):
    """List orders for the current user and create new orders."""
    permission_classes = [IsAuthenticated, IsCustomerForCreate, NotOrderingOwnOffer]
  
    def get_queryset(self):
        """Return orders where the user is customer or business participant."""
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )
    
    def get_serializer_class(self):
        """Use create serializer on POST; read serializer otherwise."""
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderReadSerializer

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update status, or delete a single order with checks."""
    permission_classes = [IsAuthenticated, IsOrderParticipant]
    queryset = Order.objects.select_related("customer_user", "business_user", "offer", "offer_detail")
    lookup_field = 'id'
    
    def get_serializer_class(self):
        """For PUT/PATCH return status update serializer; read otherwise."""
        # Für PATCH/PUT nur den Status-Update-Serializer verwenden
        if self.request.method in ['PUT', 'PATCH']:
            return OrderStatusUpdateSerializer
        return OrderReadSerializer
    
    def get_permissions(self):
        """Append role-based permissions for update/delete operations."""
        permissions = super().get_permissions()
        if self.request.method in ['PUT', 'PATCH']:
            permissions.append(IsBusinessUser())
        if self.request.method == 'DELETE':
            permissions.append(IsStaffOrAdminForDelete())
        return permissions

    def perform_update(self, serializer):
        """Ensure only the business user of the order can update status."""
        instance = self.get_object()
        if instance.business_user_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to update this order.")
        serializer.save()

    def update(self, request, *args, **kwargs):
        """Validate and apply status update, then return refreshed order."""
        partial = kwargs.pop('partial', request.method == 'PATCH')
        
        instance = self.get_object()
        input_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        input_serializer.is_valid(raise_exception=True)
        self.perform_update(input_serializer)

        instance.refresh_from_db()
        output_serializer = OrderReadSerializer(instance)
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete an order; protected by IsStaffOrAdminForDelete permission."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)  
    
class OrderCountView(generics.GenericAPIView):
    """Return total order count for a given business user id."""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCountSerializer
   

    def get(self, request, business_user_id):
        """Validate business user and return count of all related orders."""
        if not CustomUser.objects.filter(id=business_user_id).exists():
            raise NotFound("Business-User with this id does not exist.")  
        
        order_count = Order.objects.filter(business_user_id=business_user_id).count()
        return Response({"order_count": order_count}, status=status.HTTP_200_OK)    

class OrderCompletetdCountView(generics.GenericAPIView):
    """Return completed orders count for a given business user id."""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCountSerializer

    def get(self, request, business_user_id):
        """Validate business user and return count of completed orders only."""
        if not CustomUser.objects.filter(id=business_user_id).exists():
            raise NotFound("Business-User with this id does not exist.")  
        
        order_count = Order.objects.filter(business_user_id=business_user_id, status=Order.OrderStatus.COMPLETED).count()
        return Response({"completed_order_count": order_count}, status=status.HTTP_200_OK)
