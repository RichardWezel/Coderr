from django.urls import path, include
from .views import ReviewView, ReviewDetailView

app_name = 'reviews_app'
urlpatterns = [
    path('reviews/', ReviewView.as_view(), name='reviews-list-create'),
    path('reviews/<int:id>/', ReviewDetailView.as_view(), name='review-detail'),
]
