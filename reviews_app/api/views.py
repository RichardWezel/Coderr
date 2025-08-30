from rest_framework import generics, permissions
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.api.permissions import OneReviewPerBusinessUserPermission
from django_filters.rest_framework import DjangoFilterBackend

class ReviewView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OneReviewPerBusinessUserPermission]
    ordering_fields = ['updated_at', 'rating']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['business_user_id', 'reviewer_id']
    