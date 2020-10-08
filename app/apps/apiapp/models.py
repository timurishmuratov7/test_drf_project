from django.db import models
from django.core.validators import FileExtensionValidator
from .validators import file_size_validator
from taggit.managers import TaggableManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit


class Album(models.Model):
    album_name = models.CharField(max_length=200)
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )
    date_created = models.DateField(auto_now=True)
    num_of_photos = models.IntegerField(default=0)

    def __str__(self):
        return self.album_name


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now=True)
    file = models.ImageField(upload_to='original_photos',
                             validators=[FileExtensionValidator(allowed_extensions=[
                                                                'jpg',
                                                                'jpeg',
                                                                'png']),
                                         file_size_validator])
    thumbnail = ProcessedImageField(upload_to='thumbnails',
                                    processors=[ResizeToFit(150, 150)],
                                    format='JPEG')
    photo_name = models.CharField(max_length=200)
    tags = TaggableManager(blank=True)

    def get_tags(self):
        return self.tags.names()

    def get_album_name(self):
        return self.album.album_name

    def __str__(self):
        return self.photo_name
