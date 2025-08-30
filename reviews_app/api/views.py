from rest_framework import generics, permissions
from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer, ReviewDetailSerializer
from reviews_app.api.permissions import OneReviewPerBusinessUserPermission, IsReviewerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status

class ReviewView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OneReviewPerBusinessUserPermission]
    ordering_fields = ['updated_at', 'rating']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['business_user_id', 'reviewer_id']

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OneReviewPerBusinessUserPermission, IsReviewerOrReadOnly]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
       
        partial = kwargs.pop('partial', request.method == 'PATCH')
        instance = self.get_object()
        
        input_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        input_serializer.is_valid(raise_exception=True)
        self.perform_update(input_serializer)

        instance.refresh_from_db()
        output_serializer = ReviewDetailSerializer(instance)
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({}, status=status.HTTP_200_OK)  