from django.urls import path
from .views import OffersView, OfferDetailRetrieveView

app_name = 'offers_app'
urlpatterns = [
    path('offers/', OffersView.as_view(), name='offers'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetail-detail'),
]