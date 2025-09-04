from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.http import Http404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied, ParseError

from offers_app.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from .pagination import OffersGetPagination
from .permissions import isOwnerOrReadOnly, isBusinessUser, isOfferCreator
from .filters import OfferFilter


def internal_error_response_500(exception):
    return Response(
        {"error": "An internal server error has occurred.", "details": str(exception)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

class OffersView(generics.ListCreateAPIView):
    queryset = Offer.objects.select_related('user').prefetch_related('details')
    serializer_class = OfferSerializer
    pagination_class = OffersGetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), isBusinessUser()]
        return [AllowAny()]

class OfferRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.select_related('user').prefetch_related('details')
    serializer_class = OfferSerializer

    def get_permissions(self):
        if self.request.method == 'PATCH' or 'PUT':
            return [IsAuthenticated(), isOwnerOrReadOnly()]
        if self.request.method == 'DELETE':
            [IsAuthenticated(), isOfferCreator()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        try:
            
            partial = kwargs.pop('partial', True)
            instance = self.get_object()

            if instance.user != request.user:
                raise PermissionDenied("You do not have permission to update this offer.")
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            self.perform_update(serializer)
            # Always return full Offer with all details after update
            output_serializer = OfferSerializer(
                instance,
                context={**self.get_serializer_context(), 'force_full_details': True}
            )
            return Response(output_serializer.data, status=status.HTTP_200_OK)

        except (PermissionDenied, NotFound, ValidationError, ParseError, Http404) as e:
            raise e 
        except Exception as e:
            return internal_error_response_500(e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.user != request.user:
                raise PermissionDenied("You do not have permission to delete this offer.")
            self.perform_destroy(instance)
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except (PermissionDenied, NotFound, ValidationError, ParseError, Http404) as e:
            raise e
        except Exception as e:
            return internal_error_response_500(e)

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.select_related('offer', 'offer__user')
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
