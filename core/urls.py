from django.urls import path
from .views import AlbumDetailView, ImageUploadView,DeleteUpdateAlbumView,ListAllAlbumView,ListCreateAlbumView

urlpatterns = [

    path('list-albums/', ListAllAlbumView.as_view(), name='list-albums'),

    path('album-detail/<str:album_id>/', AlbumDetailView.as_view(), name='album-detail'),
    
    path('list-create-album/', ListCreateAlbumView.as_view(), name='list-create-album'),
    path('update-delete-album/<int:pk>/',DeleteUpdateAlbumView.as_view(),name='delete-update'),

    #Endpoint to post image to an album
    path('upload-image/<str:album_id>/', ImageUploadView.as_view(), name='album'),
]