from django_filters import rest_framework as filters
from ..models import Offer

class OfferFilter(filters.FilterSet):
    creator_id = filters.NumberFilter(field_name='user', lookup_expr='exact')
    max_delivery_time = filters.NumberFilter(field_name='delivery_time', lookup_expr='lte')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'min_delivery_time']

       