from django.urls import path
from .views import ProfileDetailView as Profile
from .views import BussinessProfileView as BusinessProfiles
from .views import CustomerProfileView as CustomerProfiles
from .views import FileUploadView

urlpatterns = [
    path('profile/<int:pk>/', Profile.as_view(), name='profile'),
    path('profile/business/', BusinessProfiles.as_view(), name='business-profile'),
    path('profile/customer/', CustomerProfiles.as_view(), name='customer-profile'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]

