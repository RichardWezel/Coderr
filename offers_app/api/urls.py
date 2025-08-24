from django.urls import path
from .views import OffersView, OfferRetrieveUpdateDeleteView, OfferDetailRetrieveView

app_name = 'offers_app'
urlpatterns = [
    path('offers/', OffersView.as_view(), name='offers'),
    path('offers/<int:pk>/', OfferRetrieveUpdateDeleteView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetail-detail'),
]