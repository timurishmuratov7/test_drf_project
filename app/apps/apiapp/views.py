from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from . import serializers
from registerapp.serializers import EmptySerializer
from .utils import (create_album_in_db, delete_album_in_db,
                    update_album_in_db, filter_photos_by_albums,
                    delete_photo_in_db, edit_photo_in_db,
                    get_album_list, get_one_album, get_photos,
                    get_photo_instance, filter_and_sort_photos)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AlbumViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(operation_description="Create" +
                                               " one album instance",
                         query_serializer=serializers.AlbumCreationSerializer,
                         responses={201:serializers.AlbumSerializer,
                                    400:"Bad request or the album with" +
                                        " this name already exists"})
    @action(methods=['POST'], detail=False)
    def create_album(self, request):
        serializer = serializers.AlbumCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.custom_validate(request.data, request.user)
        album = create_album_in_db(**serializer.validated_data,
                                   author=request.user)
        data = serializers.AlbumSerializer(album).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_description="Delete" +
                                               " the album instance",
                         query_serializer=serializers.AlbumNameSerializer,
                         responses={200:"Successfully deleted",
                                    400:"Bad request or the album with" +
                                        " this name does not exist"})
    @action(methods=['POST'], detail=False)
    def delete_album(self, request):
        serializer = serializers.AlbumNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.custom_validate(request.data, request.user)
        delete_album_in_db(**serializer.validated_data, author=request.user)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Edit" +
                                               " the album name",
                         query_serializer=serializers.AlbumUpdateSerializer,
                         responses={200:"Successfully edited",
                                    400:"Bad request or the album with" +
                                        " this name does not exist"})
    @action(methods=['POST'], detail=False)
    def edit_album(self, request):
        serializer = serializers.AlbumUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.custom_validate(request.data, request.user)
        album = update_album_in_db(**serializer.validated_data,
                                   author=request.user)
        return Response(status=status.HTTP_200_OK)


    sort_param = openapi.Parameter('sort_param', openapi.IN_QUERY,
                                   description="Possible values:" +
                                   " date_created," +
                                   " num_of_photos",
                                   type=openapi.TYPE_STRING)
    sort_order = openapi.Parameter('sort_order', openapi.IN_QUERY,
                                   description="Possible values:" +
                                   " + or - ",
                                   type=openapi.TYPE_STRING)
    @swagger_auto_schema(operation_description="Get" +
                                               " the list of albums",
                         query_serializer=serializers.GetAlbumListSerializer,
                         manual_parameters = [sort_param, sort_order],
                         responses={200:serializers.AlbumSerializer,
                                    400:"The sort_param or sort_order" +
                                        " were provided incorrectly."})
    @action(methods=['POST'], detail=False)
    def album_list(self, request):
        serializer = serializers.GetAlbumListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        albums = get_album_list(**serializer.validated_data,
                                author=request.user)
        data = serializers.AlbumSerializer(albums, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Get" +
                                               " a particular album" +
                                               " with photos in it",
                         query_serializer=serializers.AlbumNameSerializer,
                         responses={" 200":serializers.AlbumSerializer,
                                    "    ":serializers.PhotoSerializer,
                                    "400":"Bad request or the album with" +
                                        " this name does not exist"})
    @action(methods=['POST'], detail=False)
    def get_album(self, request):
        serializer = serializers.AlbumNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.custom_validate(request.data, request.user)
        album = get_one_album(**serializer.validated_data,
                              author=request.user)
        photos = get_photos(**serializer.validated_data,
                            author=request.user)
        photos_data = serializers.PhotoSerializer(photos, many=True).data
        album_data = serializers.AlbumSerializer(album).data
        data = {"album": album_data, "photos": photos_data}
        return Response(data=data, status=status.HTTP_200_OK)


class PhotoViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @swagger_auto_schema(operation_description="Upload a photo",
                         request_body=serializers.PhotoValidSerializer,
                         responses={201:serializers.PhotoCreationSerializer,
                                    400:"Bad request"})
    @action(methods=['POST'], detail=False)
    def upload_photo(self, request):
        validation_serializer = serializers.PhotoValidSerializer(data=request.data)
        validation_serializer.is_valid(raise_exception=True)
        validation_serializer.custom_validate(request.data, request.user)
        album_instance = get_one_album(validation_serializer.validated_data.get('album_name'),
                                       request.user)
        request.data['album'] = album_instance.pk
        serializer = serializers.PhotoCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(operation_description="Delete" +
                                               " a particular photo",
                         query_serializer=serializers.PhotoBasicSerializer,
                         responses={200:"Photo was" +
                                        " sucessfully deleted!",
                                    400:"Bad request"})
    @action(methods=['POST'], detail=False)
    def delete_photo(self, request):
        serializer = serializers.PhotoBasicSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.custom_validate(request.data, request.user)
        album_instance = get_one_album(serializer.validated_data.get('album_name'),
                                       request.user)
        delete_photo_in_db(photo_name=request.data.get('photo_name'),
                           album=album_instance)
        return Response(data={"sucess":
                              "Photo was" +
                              " sucessfully deleted!"},
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Edit" +
                                               " a particular photo",
                         query_serializer=serializers.PhotoEditSerializer,
                         responses={200:serializers.PhotoSerializer,
                                    400:"Bad request"})
    @action(methods=['POST'], detail=False)
    def edit_photo(self, request):
        serializer = serializers.PhotoEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.custom_validate(request.data, request.user)
        photo = serializer.update(serializer.validated_data)
        photo_data = serializers.PhotoSerializer(photo).data
        return Response(data=photo_data, status=status.HTTP_200_OK)

    sort_param = openapi.Parameter('sort_param', openapi.IN_QUERY,
                                   description="Possible values:" +
                                   " date_added, album or blank",
                                   type=openapi.TYPE_STRING)
    sort_order = openapi.Parameter('sort_order', openapi.IN_QUERY,
                                   description="Possible values:" +
                                   " + or - or blank",
                                   type=openapi.TYPE_STRING)
    filter_param = openapi.Parameter('filter_param', openapi.IN_QUERY,
                                   description="Possible values:" +
                                   " tags, albums or blank",
                                   type=openapi.TYPE_STRING)
    albums = openapi.Parameter('albums', openapi.IN_QUERY,
                                   description="Possible values" +
                                   " are names of albums",
                                   type=openapi.TYPE_STRING)
    tags = openapi.Parameter('tags', openapi.IN_QUERY,
                                   description="Possible values are" +
                                   " tags",
                                   type=openapi.TYPE_STRING)
    @swagger_auto_schema(operation_description="Get" +
                                               " the list of photos",
                         query_serializer=serializers.PhotoListSerializer,
                         manual_parameters = [sort_param, sort_order,
                                              filter_param, albums, tags],
                         responses={200:serializers.PhotoSerializer,
                                    400:"Bad request"})
    @action(methods=['POST'], detail=False)
    def get_photos(self, request):
        serializer = serializers.PhotoListSerializer(data=request.data)
        serializer.custom_validate(request.data, request.user)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        photos = filter_and_sort_photos(data, request.user)
        photos_data = serializers.PhotoSerializer(photos, many=True).data
        return Response(data=photos_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Get" +
                                               " a particular photo",
                         query_serializer=serializers.PhotoBasicSerializer,
                         responses={200:serializers.PhotoSerializer,
                                    400:"Bad request"})
    @action(methods=['POST'], detail=False)
    def get_photo(self, request):
        serializer = serializers.PhotoBasicSerializer(data=request.data)
        serializer.custom_validate(request.data, request.user)
        serializer.is_valid(raise_exception=True)
        photo = get_photo_instance(author=request.user,
                                   photo_name=serializer.validated_data.get("photo_name"),
                                   album_name=serializer.validated_data.get("album_name"))
        photo_data = serializers.PhotoSerializer(photo).data
        return Response(data=photo_data, status=status.HTTP_200_OK)
