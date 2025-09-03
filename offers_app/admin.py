from django.contrib import admin
from offers_app.models import Offer, OfferDetail

admin.site.site_header = "Offers Administration"
admin.site.site_title = "Offers"

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'title', 'image', 'description',
        'min_price', 'min_delivery_time', 'created_at', 'updated_at'
    )
    search_fields = (
        'title', 'description', 'user__username', 'user__email'
    )
    list_filter = ('min_price', 'min_delivery_time')
    ordering = ('id',)
    list_select_related = ('user',)

@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'offer', 'title', 'offer_type',
        'price', 'revisions', 'delivery_time_in_days', 'features_display'
    )
    search_fields = (
        'title', 'offer__title', 'offer__user__username', 'offer__user__email'
    )
    list_filter = ('offer_type', 'revisions', 'price')
    ordering = ('id',)
    autocomplete_fields = ('offer',)
    list_select_related = ('offer',)

    def features_display(self, obj):
        """Readable, truncated features list for admin change list."""
        feats = obj.features or []
        if not isinstance(feats, list):
            return str(feats)
        if not feats:
            return "-"
        shown = ', '.join(map(str, feats[:3]))
        extra = len(feats) - 3
        return shown if extra <= 0 else f"{shown} …(+{extra})"
    features_display.short_description = 'Features'
