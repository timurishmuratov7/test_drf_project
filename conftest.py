import pytest
import uuid

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from apiapp.models import Album, Photo
from django.urls import reverse

@pytest.fixture
def test_password():
   return 'strong-test-pass'


@pytest.fixture
def create_user(db, django_user_model, test_password):
   def make_user(**kwargs):
       kwargs['password'] = test_password
       if 'username' not in kwargs:
           kwargs['username'] = str(uuid.uuid4())
       return django_user_model.objects.create_user(**kwargs)
   return make_user

@pytest.fixture
def api_client():
   return APIClient()

@pytest.fixture
def get_or_create_token(db, create_user):
   user = create_user()
   token, _ = Token.objects.get_or_create(user=user)
   return token

@pytest.fixture
def api_client_with_credentials(
   db, logged_in_client, api_client
):
   user = logged_in_client
   api_client.force_authenticate(user=user)
   yield api_client
   api_client.force_authenticate(user=None)

@pytest.fixture
def logged_in_client(db, django_user_model, client):
    user = django_user_model.objects.create_user(username="newuser",
                                                 password="newpassword")
    client.login(username="newuser", password="newpassword")
    return user

@pytest.fixture
def existing_album(db, logged_in_client):
    return Album.objects.create(album_name="existingalbum", author=logged_in_client)

@pytest.fixture
def existing_photo(db, logged_in_client, existing_album):
    return Photo.objects.create(album=existing_album, photo_name = "existingphoto")

@pytest.fixture
def existing_albums(db, logged_in_client):
    def create_album():
        existing_albums = ["existingalbum", "existingalbum1", "existingalbum2"]
        num_of_photos = 0
        for album_name in existing_albums:
            Album.objects.create(album_name=album_name, author=logged_in_client,
                                 num_of_photos=num_of_photos)
            num_of_photos += 1
        return Album.objects.filter(author = logged_in_client).all()
    return create_album()

@pytest.fixture
def proper_login(api_client):
    data = {
        "email": "newuser",
        "password": "newpassword"
    }
    url = reverse('auth-login')
    response = api_client.post(url, data=data, format = 'json')
