from rest_framework import serializers
from .models import Album, Image
from auth_service.serializer import UserSerializer
from drf_spectacular.utils import extend_schema_field


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image_url', 'file_name', 'created_at', 'imageId']
        read_only_fields = ['imageId', 'created_at']



class AlbumSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True,source='image_set')
    organizer = UserSerializer(read_only=True)
    image_count = serializers.SerializerMethodField()
    class Meta:
        model = Album
        fields = ['id', 'organizer', 'title','description','event_type','event_date', 'created_at', 'albumId', 'images','album_picture','image_count']
        read_only_fields = ['albumId', 'created_at'] 

    @extend_schema_field(int)
    def get_image_count(self, obj):
        return obj.image_set.count()

