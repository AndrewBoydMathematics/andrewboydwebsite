from rest_framework import serializers
from .models import Artwork, CommissionRequest

class ArtworkSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    medium_display = serializers.CharField(source='get_medium_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Artwork
        fields = ['id', 'title', 'description', 'image', 'tile_image', 'thumbnail_image', 'status', 'status_display', 
                 'price', 'medium', 'medium_display', 'category', 'category_display', 
                 'created_at', 'updated_at']

class CommissionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRequest
        fields = '__all__'
        read_only_fields = ('status',) 