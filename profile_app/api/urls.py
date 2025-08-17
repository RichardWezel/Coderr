from django.urls import path
from .views import ProfileDetailView as Profile
from .views import FileUploadView

urlpatterns = [
    path('profile/<int:pk>/', Profile.as_view(), name='profile'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]

