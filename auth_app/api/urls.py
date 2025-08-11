from django.urls import path, include
from .views import RegistrationView, LoginView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]