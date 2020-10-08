import pytest
from django.urls import reverse
from apiapp.models import Album, Photo
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

@pytest.mark.slow
@pytest.mark.django_db
@pytest.mark.parametrize(
    "album_name, photo_name, tags, height, status_code", [
       ("", "easyphoto", "", 128, 400),
       ("existingalbum", "", "", 128, 400),
       ("existingalbum", "existingphoto", "", 128, 400),
       ("existingalbum", "newphoto", "cars, photo", 200, 201),
       ("existingalbum", "newphoto", "cars, photo", 20000, 400),
    ]
)
def test_upload_photo_api(api_client_with_credentials, logged_in_client, existing_album, existing_photo,
                        album_name, photo_name, tags, height, status_code):
    url = reverse('photo-upload-photo')
    width = height
    valid_solid_color_jpeg = Image.new(mode='RGB', size=(width, height), color='red')
    valid_solid_color_jpeg.save('red_image.jpeg', "JPEG")
    file = SimpleUploadedFile("test_image.jpeg", content=open('red_image.jpeg', 'rb').read(), content_type="image/jpg")
    data = {
        "album_name": album_name,
        "photo_name": photo_name,
        "tags": tags,
        "file": file
    }
    response = api_client_with_credentials.post(url, data=data, format='multipart')
    assert status_code == response.status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "album_name, photo_name, status_code", [
       ("", "easyphoto", 400),
       ("existingalbum", "", 400),
       ("existingalbum", "existingphoto", 200),
       ("existingalbum", "newphoto", 400),
       ("newalbum", "newphoto", 400),
    ]
)
def test_delete_photo_api(api_client_with_credentials, logged_in_client, existing_album, existing_photo,
                        album_name, photo_name, status_code):
    url = reverse('photo-delete-photo')
    data = {
        "album_name": album_name,
        "photo_name": photo_name,
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "album_name, photo_name, new_photo_name, tags, status_code", [
       ("", "existingphoto", "newphoto", "", 400),
       ("existingalbum", "existingphoto", "newphoto", "some tags", 200),
       ("existingalbum", "newphoto", "newphoto1", "tags, easy", 400),
       ("existingalbum", "", "newphoto", "tags, easy", 400),
       ("newalbum", "existingphoto", "newphoto", "tags, easy", 400),
    ]
)
def test_edit_photo_api(api_client_with_credentials, logged_in_client, existing_album, existing_photo,
                        album_name, photo_name, new_photo_name, tags, status_code):
    url = reverse('photo-edit-photo')
    data = {
        "album_name": album_name,
        "photo_name": photo_name,
        "new_photo_name": new_photo_name,
        "tags": tags
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code



@pytest.mark.django_db
@pytest.mark.parametrize(
    "album_name, photo_name, status_code", [
       ("", "existingphoto", 400),
       ("existingalbum", "existingphoto", 200),
       ("existingalbum", "newphoto", 400),
       ("existingalbum", "", 400),
    ]
)
def test_get_photo_api(api_client_with_credentials, logged_in_client, existing_album, existing_photo,
                        album_name, photo_name, status_code):
    url = reverse('photo-get-photo')
    data = {
        "album_name": album_name,
        "photo_name": photo_name,
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "sort_param, sort_order, filter_param, albums, tags, status_code", [
       ("", "", "", "", "", 200),
       ("date_added", "+", "tags", "some tags", "", 400),
       ("something", "", "tags", "some tags", "", 400),
       ("album", "-", "albums", "existingalbum", "", 200),
       ("date_added", "+", "something", "", "", 400),
       ("album", "-", "tags", "existingalbum", "some tags", 200),
    ]
)
def test_list_albums_api(api_client_with_credentials, logged_in_client, existing_albums, sort_param,
                        sort_order, filter_param, albums, tags, status_code):
    url = reverse('photo-get-photos')
    data = {
        "sort_param": sort_param,
        "sort_order": sort_order,
        "filter_param": filter_param,
        "tags": tags,
        "albums": albums
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code
