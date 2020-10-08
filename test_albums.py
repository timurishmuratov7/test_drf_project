import pytest
from django.urls import reverse
from apiapp.models import Album


@pytest.mark.django_db
@pytest.mark.parametrize(
    "album_name, status_code", [
       ("", 400),
       ("existingalbum", 400),
       ("newalbum", 201),
    ]
)
def test_create_album_api(api_client_with_credentials, logged_in_client, existing_album, album_name, status_code):
    url = reverse('album-create-album')
    data = {
        "album_name": album_name,
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "album_name, status_code", [
       ("", 400),
       ("existingalbum", 200),
       ("newalbum", 400),
    ]
)
def test_delete_album_api(api_client_with_credentials, logged_in_client, existing_album, album_name, status_code):
    url = reverse('album-delete-album')
    data = {
        "album_name": album_name,
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code

@pytest.mark.django_db
@pytest.mark.parametrize(
    "album_name, new_album_name, status_code", [
       ("", "something", 400),
       ("existingalbum", "", 400),
       ("existingalbum", "newalbum", 200),
    ]
)
def test_edit_album_api(api_client_with_credentials, logged_in_client, existing_album, album_name, new_album_name, status_code):
    url = reverse('album-edit-album')
    data = {
        "album_name": album_name,
        "new_album_name": new_album_name
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code

@pytest.mark.django_db
@pytest.mark.parametrize(
    "sort_param, sort_order, expected_names, status_code", [
       ("", "", ["existingalbum", "existingalbum1", "existingalbum2"], 200),
       ("date_created", "+", ["existingalbum", "existingalbum1", "existingalbum2"], 200),
       ("num_of_photos", "+", ["existingalbum", "existingalbum1", "existingalbum2"], 200),
       ("num_of_photos", "-", ["existingalbum2", "existingalbum1", "existingalbum"], 200),
    ]
)
def test_list_albums_api(api_client_with_credentials, logged_in_client, existing_albums, sort_param, sort_order, expected_names, status_code):
    url = reverse('album-album-list')
    data = {
        "sort_param": sort_param,
        "sort_order": sort_order
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code
    albums = response.data
    names_sorted = []
    for x in albums:
        names_sorted.append(x.get('album_name'))
    print("RESPONSE NAMES", names_sorted)
    assert names_sorted == expected_names


@pytest.mark.django_db
@pytest.mark.parametrize(
    "album_name, status_code", [
       ("", 400),
       ("existingalbum", 200),
       ("newalbum", 400),
    ]
)
def test_delete_album_api(api_client_with_credentials, logged_in_client, existing_album, album_name, status_code):
    url = reverse('album-get-album')
    data = {
        "album_name": album_name,
    }
    response = api_client_with_credentials.post(url, data=data, format='json')
    assert status_code == response.status_code
