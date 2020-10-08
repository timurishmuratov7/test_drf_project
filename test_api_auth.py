import pytest
from django.urls import reverse
from registerapp.utils import create_user_account


from django.contrib.auth.models import User

@pytest.mark.django_db
def test_user_create():
  create_user_account('lennon@thebeatles.com', 'johnpassword')
  assert User.objects.count() == 1

@pytest.mark.django_db
@pytest.mark.parametrize(
   "email, password, status_code", [
       ("", "", 400),
       ("", "strong_pass", 400),
       ("user@example.com", "", 400),
       ("user@example.com", "invalid_pass", 400),
       ("lennon@thebeatles.com", "johnpassword", 200),
   ]
)
def test_login_data_validation(
   email, password, status_code, api_client
):
   user = create_user_account("lennon@thebeatles.com", "johnpassword")
   data = {
       "email": email,
       "password": password
   }
   url = reverse('auth-login')
   response = api_client.post(url, data=data, format = 'json')
   assert status_code == response.status_code

@pytest.mark.django_db
def test_logout(api_client_with_credentials, proper_login):
      url = reverse('auth-logout')
      response = api_client_with_credentials.post(url)
      assert response.status_code == 200
