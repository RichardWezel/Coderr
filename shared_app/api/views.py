from rest_framework import permissions, status, generics
from rest_framework.response import Response
from django.db.models import Avg

from reviews_app.models import Review
from auth_app.models import CustomUser
from offers_app.models import Offer
from .serializers import BaseInfoSerializer

class BaseInfoView(generics.GenericAPIView):
    """
    View to retrieve base information about the platform.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = BaseInfoSerializer

    def get(self, request):
        avg = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0.0

        data = {
            "review_count": Review.objects.count(),
            "average_rating": round(float(avg), 2),
            "business_profile_count": CustomUser.objects.filter(
                type=CustomUser.Roles.BUSINESS
            ).count(),
            "offer_count": Offer.objects.count(),
        }

        # dict als "instance" reinreichen → kein is_valid() nötig
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
