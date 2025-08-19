from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include(('auth_app.api.urls', 'auth_app'), namespace='auth_app')),
    path('api/', include(('profile_app.api.urls', 'profile_app'), namespace='profile_app')),
    path('api/', include(('offers_app.api.urls', 'offers_app'), namespace='offers')),
    path('api/', include(('reviews_app.api.urls', 'reviews_app'), namespace='reviews_app')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
