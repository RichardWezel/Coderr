from django.urls import path, include
from .views import ReviewView

app_name = 'reviews_app'
urlpatterns = [
    path('reviews/', ReviewView.as_view(), name='reviews-list-create')
]
