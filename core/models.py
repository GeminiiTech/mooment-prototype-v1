from django.db import models
import random
import os
from uuid import uuid4
from auth_service.models import MyUser
from django.core.files.storage import default_storage
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Create your models here.

def upload_image_to(instance, filename):
    # Extract the file extension (e.g., .jpg, .png)
    extension = os.path.splitext(filename)[1]  

    # Create a unique file name using UUID
    new_filename = f"{uuid4().hex}{extension}"  

    # Return the path where the file should be saved
    return f"uploads/albums/{instance.album.organizer.first_name} {instance.album.organizer.last_name}/{instance.album.albumId}/{new_filename}"


class Album(models.Model):
    organizer = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=100)
    description = models.TextField(default='No description provided')
    created_at = models.DateTimeField(auto_now_add=True)
    albumId = models.CharField(max_length=6, unique=True)
    event_date = models.DateField(null=True, blank=True)
    event_type = models.CharField(max_length=100, default='No event type provided')
    album_picture = models.ImageField(upload_to='albums-pictures/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.albumId:
            self.albumId = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            albumId = f"{random.randint(100000, 999999)}"  # Generate a random 6-digit number
            if not Album.objects.filter(albumId=albumId).exists():  # Ensure it's unique
                return albumId

    def delete(self, *args, **kwargs):
        """ Delete the album picture from S3 before deleting the Album instance """
        if self.album_picture:
            default_storage.delete(self.album_picture.name)
        super().delete(*args, **kwargs)        

    def __str__(self):
        return self.title
    
class Image(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to=upload_image_to)
    file_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    imageId = models.CharField(max_length=6, unique=True)

    def save(self, *args, **kwargs):
        if not self.imageId:
            self.imageId = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            imageId = f"{random.randint(100000, 999999)}"  # Generate a random 6-digit number
            if not Image.objects.filter(imageId=imageId).exists():  # Ensure it's unique
                return imageId
            
    def __str__(self):
        return self.image_url.url 
    
    def delete(self, *args, **kwargs):
        """ Delete the image file from S3 when the Image instance is deleted """
        if self.image_url:
            default_storage.delete(self.image_url.name)
        super().delete(*args, **kwargs)
        

# 🔥 Automatically delete all images related to an album when the album is deleted
@receiver(post_delete, sender=Album)
def delete_related_images(sender, instance, **kwargs):
    """ Deletes all images associated with the deleted album from S3 """
    images = Image.objects.filter(album=instance)
    for image in images:
        if image.image_url:
            default_storage.delete(image.image_url.name)
        image.delete()