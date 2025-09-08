from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework import generics, permissions, status

from reviews_app.models import Review
from .serializers import ReviewSerializer, ReviewDetailSerializer
from .permissions import OneReviewPerBusinessUserPermission, IsReviewerOrReadOnly, IsCustomerUser



class ReviewView(generics.ListCreateAPIView):
    """List reviews and allow authenticated customers to create one per business."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OneReviewPerBusinessUserPermission, IsCustomerUser]
    ordering_fields = ['updated_at', 'rating']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['business_user_id', 'reviewer_id']

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a review with reviewer-only write access."""
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OneReviewPerBusinessUserPermission, IsReviewerOrReadOnly]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        """Apply partial/full updates; return refreshed review payload."""
       
        partial = kwargs.pop('partial', request.method == 'PATCH')
        instance = self.get_object()
        
        input_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        input_serializer.is_valid(raise_exception=True)
        self.perform_update(input_serializer)

        instance.refresh_from_db()
        output_serializer = ReviewDetailSerializer(instance)
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete the review and return an empty JSON object."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({}, status=status.HTTP_200_OK)  
