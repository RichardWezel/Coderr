from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer, OfferDetailSerializer
from offers_app.api.pagination import OffersGetPagination
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class OffersView(generics.ListCreateAPIView):
    queryset = Offer.objects.select_related('user').prefetch_related('details')
    serializer_class = OfferSerializer
    pagination_class = OffersGetPagination
    permission_classes = [IsAuthenticated]  
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__id', 'min_price', 'max_delivery_time', 'page_size']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

class OfferRetrieveView(generics.RetrieveAPIView):
    queryset = Offer.objects.select_related('user').prefetch_related('details')
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.select_related('offer', 'offer__user')
    serializer_class = OfferDetailSerializer  # oder dein *Full*-Serializer
    permission_classes = [IsAuthenticated]