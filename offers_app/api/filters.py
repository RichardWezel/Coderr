from django_filters import rest_framework as filters
from django.db.models import Q
from ..models import Offer


class OfferFilter(filters.FilterSet):
    """Filter offers by creator, minimum price (>=), and max delivery time (<=)."""

    creator_id = filters.NumberFilter(field_name='user', lookup_expr='exact')
    min_price = filters.NumberFilter(field_name='min_price', lookup_expr='gte')
    # Include offers with unknown (NULL) delivery time as well
    max_delivery_time = filters.NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'min_delivery_time']

    def filter_max_delivery_time(self, queryset, name, value):
        """Filter offers where min_delivery_time <= value, including NULL values.

        This treats unknown delivery times as eligible for a max constraint.
        """
        if value is None:
            return queryset
        return queryset.filter(Q(min_delivery_time__lte=value) | Q(min_delivery_time__isnull=True))

      
