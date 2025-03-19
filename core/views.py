from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Album, Image
from .serializers import AlbumSerializer, ImageSerializer
import logging

logger = logging.getLogger(__name__)

class AlbumDetailView(APIView):
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    """
    API view to get a specific album.
    """
    def get(self, request, album_id, *args, **kwargs):
        try:
            album = Album.objects.get(albumId=album_id)
            serializer = AlbumSerializer(album)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Album.DoesNotExist:
            logger.info("Album with albumId %s not found.", album_id)
            return Response({"error": "Album not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Unexpected error retrieving album %s: %s", album_id, str(e), exc_info=True)
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListAllAlbumView(APIView):
    """
    API view to retrieve all albums.
    """
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            albums = Album.objects.all()
            serializer = AlbumSerializer(albums, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error listing all albums: %s", str(e), exc_info=True)
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListCreateAlbumView(APIView):
    """
    API view to get all albums related to the current user
    OR create a new album.
    """
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        try:
            albums = Album.objects.filter(organizer=request.user)
            serializer = AlbumSerializer(albums, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error retrieving albums for user %s: %s", request.user, str(e), exc_info=True)
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            album_picture = request.FILES.get('album_picture', None)
            serializer = AlbumSerializer(data=data)
            if serializer.is_valid():
                album = serializer.save(organizer=request.user)
                if album_picture:
                    album.album_picture = album_picture
                    album.save()
                return Response(AlbumSerializer(album).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error creating album: %s", str(e), exc_info=True)
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteUpdateAlbumView(APIView):
    """
    API view to delete or edit an album.
    """
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
            album.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except Album.DoesNotExist:
            logger.info("Attempt to delete non-existent album with pk %s.", pk)
            return Response({"error": "Album not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error deleting album %s: %s", pk, str(e), exc_info=True)
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            album = Album.objects.get(pk=pk)
            serializer = AlbumSerializer(album, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Album.DoesNotExist:
            logger.info("Attempt to update non-existent album with pk %s.", pk)
            return Response({"error": "Album not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error updating album %s: %s", pk, str(e), exc_info=True)
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageUploadView(APIView):
    serializer_class = ImageSerializer

    def post(self, request, album_id):
        """
        Handle uploading multiple images to an album.
        """
        try:
            album = Album.objects.get(albumId=album_id)
        except Album.DoesNotExist:
            logger.info("Album with albumId %s not found for image upload.", album_id)
            return Response({"error": "Album not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error retrieving album %s: %s", album_id, str(e), exc_info=True)
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        uploaded_files = request.FILES.getlist("files")
        if not uploaded_files:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for uploaded_file in uploaded_files:
            try:
                image_instance = Image(
                    album=album,
                    image_url=uploaded_file,  # This field should be a FileField or ImageField
                    file_name=uploaded_file.name
                )
                image_instance.save()
                created_images.append(ImageSerializer(image_instance).data)
            except Exception as e:
                logger.error("Error saving image %s for album %s: %s", uploaded_file.name, album_id, str(e), exc_info=True)
                # Optionally: Continue processing other files or break out

        return Response({"images": created_images}, status=status.HTTP_201_CREATED)
