from rest_framework import serializers
from .models import Album, Image
from auth_service.serializer import UserSerializer


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image_url', 'file_name', 'created_at', 'imageId']
        read_only_fields = ['imageId', 'created_at']



class AlbumSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True,source='image_set')
    organizer = UserSerializer(read_only=True)
    class Meta:
        model = Album
        fields = ['id', 'organizer', 'title','description','visibility', 'created_at', 'albumId', 'images','album_picture']
        read_only_fields = ['albumId', 'created_at'] 

