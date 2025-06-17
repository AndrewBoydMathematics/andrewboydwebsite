from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from artwork import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('artwork.urls')),
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('commission/', views.commission, name='commission'),
    path('models/', views.models, name='models'),
    path('artwork/<int:artwork_id>/', views.artwork_detail, name='artwork_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 