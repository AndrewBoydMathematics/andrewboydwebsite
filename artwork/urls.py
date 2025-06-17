from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'artwork', views.ArtworkViewSet)
router.register(r'commissions', views.CommissionRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('commission/', views.commission, name='commission'),
    path('artwork/<int:artwork_id>/', views.artwork_detail, name='artwork_detail'),
    path('payment/success/', views.payment_success, name='payment_success'),
] 