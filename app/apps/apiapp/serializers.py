from rest_framework import serializers
from .models import Album
from .models import Photo
import taggit

# Albums


class AlbumCreationSerializer(serializers.ModelSerializer):

    def custom_validate(self, validated_data, user):
        existing_album = Album.objects.filter(album_name=validated_data.get("album_name"),
                                              author=user)
        if existing_album.exists():
            raise serializers.ValidationError({"detail":
                                               "Album with this name" +
                                               " already exists"})

    class Meta:
        model = Album
        fields = ('album_name',)


class AlbumNameSerializer(serializers.Serializer):
    album_name = serializers.CharField(max_length=200, required=True)

    def custom_validate(self, validated_data, user):
        try:
            Album.objects.get(album_name=validated_data.get("album_name"),
                              author=user).pk
        except:
            raise serializers.ValidationError({"detail":
                                               "Album with" +
                                               " this name does not exist"})


class AlbumUpdateSerializer(serializers.Serializer):
    album_name = serializers.CharField(max_length=200, required=True)
    new_album_name = serializers.CharField(max_length=200, required=True)

    def custom_validate(self, validated_data, user):
        try:
            Album.objects.get(album_name=validated_data.get("album_name"),
                              author=user).pk
        except:
            raise serializers.ValidationError({"detail":
                                               "Album with this name" +
                                               " does not exist"})


class GetAlbumListSerializer(serializers.Serializer):
    sort_param = serializers.CharField(max_length=200, allow_blank=True)
    sort_order = serializers.CharField(max_length=10, allow_blank=True)

    def custom_validate(self, validated_data):
        sort_param = validated_data.get('sort_param')
        sort_order = validated_data.get('sort_order')
        if sort_param not in ["date_created", "num_of_photos", ""]:
            raise serializers.ValidationError({"detail":
                                               "Unknown sort parameter." +
                                               " Please, provide" +
                                               " 'date_created' or" +
                                               " 'num_of_photos' or" +
                                               " leave it blank"})
        elif sort_param in ["date_created", "num_of_photos"]:
            if sort_order not in ["+", "-"]:
                raise serializers.ValidationError({"detail":
                                                   "Unknown sort order." +
                                                   " Please, provide " +
                                                   "'+' or '-'"})


class AlbumSerializer(serializers.ModelSerializer):

    class Meta:
        model = Album
        fields = ('album_name', 'date_created', 'num_of_photos')


# Photos


class TagsField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class StringAlbumSerializer(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class PhotoCreationSerializer(serializers.ModelSerializer):
    tags = TagsField(source="get_tags")

    def create(self, validated_data):
        tags = validated_data.pop("get_tags")
        print("ALBUM NAME", validated_data.get("album"))
        album = Album.objects.get(album_name=validated_data.get("album"))
        existing_photos = Photo.objects.filter(album=album.pk).all()
        existing_names = list(existing_photos.values_list('photo_name',
                                                          flat=True))
        if validated_data.get("photo_name") in existing_names:
            raise serializers.ValidationError({"detail":
                                               "Photo with this" +
                                               " name in this album" +
                                               " already exists"})
        else:
            photo = Photo.objects.create(**validated_data)
            photo.tags.add(*taggit.utils._parse_tags(tags))
            photo.thumbnail = validated_data.get('file')
            photo.save()
            album.num_of_photos = len(existing_names) + 1
            album.save(update_fields=['num_of_photos'])
        return photo

    class Meta:
        model = Photo
        fields = ('album', 'file', 'photo_name', 'tags')


class PhotoValidSerializer(serializers.Serializer):
    album_name = serializers.CharField(max_length=200, required=True)
    photo_name = serializers.CharField(max_length=200, required=True)
    tags = serializers.CharField(max_length=200, required=False)
    file = serializers.FileField()

    def custom_validate(self, validated_data, user):
        try:
            Album.objects.get(album_name=validated_data.get("album_name"),
                              author=user).pk
            album = Album.objects.get(album_name=validated_data.get("album_name"))
        except:
            raise serializers.ValidationError({"detail":
                                               "Album with" +
                                               " this name does not exist"})


class PhotoSerializer(serializers.ModelSerializer):
    tags = TagsField(source="get_tags")
    album_name = StringAlbumSerializer(source="get_album_name")

    class Meta:
        model = Photo
        fields = ('photo_name', 'date_added',
                  'file', 'thumbnail',
                  'tags', 'album_name')


class PhotoBasicSerializer(serializers.Serializer):
    album_name = serializers.CharField(max_length=200, required=True)
    photo_name = serializers.CharField(max_length=200, required=True)

    def custom_validate(self, validated_data, user):
        try:
            Album.objects.get(album_name=validated_data.get("album_name"),
                              author=user).pk
            album = Album.objects.get(album_name=validated_data.get("album_name"))
        except:
            raise serializers.ValidationError({"detail":
                                               "Album with this name" +
                                               " does not exist"})
        existing_photos = Photo.objects.filter(album=album.pk).all()
        existing_names = list(existing_photos.values_list('photo_name',
                                                          flat=True))
        if validated_data.get('photo_name') not in existing_names:
            raise serializers.ValidationError({"detail":
                                               "Photo with" +
                                               " this name" +
                                               " does not exist"})


class PhotoEditSerializer(serializers.Serializer):
    album_name = serializers.CharField(max_length=200, required=True)
    photo_name = serializers.CharField(max_length=200, required=True)
    new_photo_name = serializers.CharField(max_length=200, allow_blank=True)
    tags = serializers.CharField(max_length=200, allow_blank=True)

    def update(self, validated_data):
        tags = validated_data.get("tags")
        album = Album.objects.get(album_name=validated_data.get("album_name"))
        existing_photos = Photo.objects.filter(album=album.pk).all()
        existing_names = list(existing_photos.values_list('photo_name',
                                                          flat=True))
        if validated_data.get("new_photo_name") in existing_names:
            raise serializers.ValidationError({"detail":
                                               "Photo with this name" +
                                               " in this album already exists"})
        else:
            photo = Photo.objects.get(album=album.pk,
                                      photo_name=validated_data.get("photo_name"))
            if tags != "":
                photo.tags.set(*taggit.utils._parse_tags(tags))
            if validated_data.get("new_photo_name") != "":
                photo.photo_name = validated_data.get("new_photo_name")
            photo.save(update_fields=['photo_name'])
        return photo

    def custom_validate(self, validated_data, user):
        new_photo_name = validated_data.get('new_photo_name')
        tags = validated_data.get('tags')
        try:
            Album.objects.get(album_name=validated_data.get("album_name"),
                              author=user).pk
            album = Album.objects.get(album_name=validated_data.get("album_name"))
        except:
            raise serializers.ValidationError({"detail":
                                               "Album with this name" +
                                               " does not exist"})
        existing_photos = Photo.objects.filter(album=album.pk).all()
        existing_names = list(existing_photos.values_list('photo_name',
                              flat=True))
        if validated_data.get('photo_name') not in existing_names:
            raise serializers.ValidationError({"detail":
                                               "Photo with this name" +
                                               " does not exist"})
        if new_photo_name == "" and tags == "":
            raise serializers.ValidationError({"detail":
                                               "You should update either" +
                                               " photo_name or tags"})


class PhotoListSerializer(serializers.Serializer):
    sort_order = serializers.CharField(max_length=200, allow_blank=True)
    sort_param = serializers.CharField(max_length=200, allow_blank=True)
    filter_param = serializers.CharField(max_length=200, allow_blank=True)
    tags = serializers.CharField(max_length=200, allow_blank=True)
    albums = serializers.CharField(max_length=200, allow_blank=True)

    def custom_validate(self, validated_data, user):
        sort_order = validated_data.get('sort_order')
        sort_param = validated_data.get('sort_param')
        filter_param = validated_data.get('filter_param')
        if sort_param not in ["date_added", "album", ""]:
            raise serializers.ValidationError({"detail":
                                               "Unknown sort" +
                                               " parameters. Please, " +
                                               "provide 'date_added'" +
                                               " or 'album' or leave" +
                                               " it blank"})
        elif sort_param in ["date_added", "album"]:
            if sort_order not in ["+", "-"]:
                raise serializers.ValidationError({"detail":
                                                   "Unknown sort order. " +
                                                   "Please, provide" +
                                                   " '+' or '-'"})
        if filter_param not in ["tags", "albums",
                                "tags, albums",
                                "albums, tags", ""]:
            raise serializers.ValidationError({"detail":
                                               "Unknown filter" +
                                               " parameters. Please, " +
                                               "provide 'tags' or" +
                                               " 'albums' or 'tags," +
                                               " albums' leave it blank"})
        albums_parsed = taggit.utils._parse_tags(validated_data.get('albums'))
        tags_parsed = taggit.utils._parse_tags(validated_data.get('tags'))
        author_albums = list(Album.objects.filter(author=user).values_list('album_name',
                                                                           flat=True))
        if (filter_param == "albums"
                or filter_param == "tags, albums"
                or filter_param == "albums, tags"):
            if albums_parsed == []:
                raise serializers.ValidationError({"detail":
                                                   "No albums were provided"})
            for album in albums_parsed:
                if album not in author_albums:
                    raise serializers.ValidationError({"detail":
                                                       "Some albums that" +
                                                       " you provided " +
                                                       "do not exist."})
        if (filter_param == "tags"
                or filter_param == "tags, albums"
                or filter_param == "albums, tags"):
            if tags_parsed == []:
                raise serializers.ValidationError({"detail":
                                                   "No tags were provided"})
