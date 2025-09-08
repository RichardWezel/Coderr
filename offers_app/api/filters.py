from django_filters import rest_framework as filters
from django.db.models import Q
from ..models import Offer


class OfferFilter(filters.FilterSet):
    """Filter offers by creator, minimum price (>=), and max delivery time (<=)."""

    creator_id = filters.NumberFilter(field_name='user', lookup_expr='exact')
    min_price = filters.NumberFilter(field_name='min_price', lookup_expr='gte')
    max_delivery_time = filters.NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def filter_max_delivery_time(self, queryset, name, value):
        """Filter offers that have at least one OfferDetail with
        delivery_time_in_days <= value. Uses DISTINCT to avoid duplicates.
        """
        if value is None:
            return queryset
        return queryset.filter(details__delivery_time_in_days__lte=value).distinct()

      
