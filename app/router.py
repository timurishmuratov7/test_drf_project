from rest_framework import routers

from apiapp.views import AlbumViewSet, PhotoViewSet
from registerapp.views import AuthViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register('auth', AuthViewSet, basename='auth')
router.register('album', AlbumViewSet, basename='album')
router.register('photo', PhotoViewSet, basename='photo')
