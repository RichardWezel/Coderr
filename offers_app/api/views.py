from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from offers_app.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from .pagination import OffersGetPagination
from .permissions import isOwnerOrReadOnly, isBusinessUser


def internal_error_response_500(exception):
    """
    Return a standardized internal server error response.

    Args:
        exception (Exception): The raised exception.

    Returns:
        Response: A DRF Response with a 500 status and error details.
    """

    return Response(
        {"error": "An internal server error has occurred.", "details": str(exception)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


class OffersView(generics.ListCreateAPIView):
    queryset = Offer.objects.select_related('user').prefetch_related('details')
    serializer_class = OfferSerializer
    pagination_class = OffersGetPagination
    permission_classes = [IsAuthenticated, isBusinessUser]  
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__id', 'min_price', 'min_delivery_time']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

class OfferRetrieveUpdateDeleteView(generics.RetrieveUpdateAPIView):
    queryset = Offer.objects.select_related('user').prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated, isOwnerOrReadOnly, isBusinessUser]

    def update(self, request, *args, **kwargs):
        try:
            
            partial = kwargs.pop('partial', True)
            instance = self.get_object()

            if instance.user != request.user:
                raise PermissionDenied("You do not have permission to update this offer.")
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (PermissionDenied, NotFound, ValidationError, Http404) as e:
            raise e 
        except Exception as e:
            return internal_error_response_500(e)

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.select_related('offer', 'offer__user')
    serializer_class = OfferDetailSerializer  # oder dein *Full*-Serializer
    permission_classes = [IsAuthenticated]