from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('auth_app.api.urls', 'auth_app'), namespace='auth_app')),
    path('api/', include(('profile_app.api.urls', 'profile_app'), namespace='profile_app')),
]
