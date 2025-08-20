from django.urls import path
from .views import OffersView, OfferRetrieveView, OfferDetailRetrieveView

app_name = 'offers_app'
urlpatterns = [
    path('offers/', OffersView.as_view(), name='offers'),
    path('offers/<int:pk>/', OfferRetrieveView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetail-detail'),
]