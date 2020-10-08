from django.contrib import admin
from .models import Album, Photo
from django.utils.safestring import mark_safe


class AlbumAdmin(admin.ModelAdmin):
    readonly_fields = ('date_created',)


class PhotoAdmin(admin.ModelAdmin):
    readonly_fields = ('date_added',)

admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
