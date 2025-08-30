from rest_framework import generics, permissions
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.api.permissions import OneReviewPerBusinessUserPermission

class ReviewView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OneReviewPerBusinessUserPermission]

    