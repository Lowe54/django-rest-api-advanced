from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
USER_GETTOKEN_URL = reverse('user:token_obtain_pair')
USER_ENDPOINT_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the users API (Public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """ Test creating new user with valid payload is successful"""

        payload = {
            "email": 'test@test.com',
            "password": "password124",
            "name": "Joe Bloggs",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_duplicate_user(self):
        """ Test creating a user that already exists, it should fail"""
        payload = {
            "email": "test@test.com",
            "password": "password1",
            "name": "duplicate",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_restriction(self):
        """Test that the password is more than 5 characters"""
        payload = {
            "email": "joe@test.com",
            "password": "123",
            "name": "Joe"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_invalid_user_or_user_not_exists_for_token_auth(self):
        """ Test that the token endpoint returns 401 if invalid user credentials
            are provided or that the user does not exist"""

        payload_invalid = {
            "email": "invalid@test.com",
            "password": "123456",
            "name": "Invalid User"
        }

        self.client.post(CREATE_USER_URL, payload_invalid)

        invalid_res = self.client.post(USER_GETTOKEN_URL,
                                       {
                                            "email": "invalid@test.com",
                                            "password": "12347"
                                       })

        unknown_user = self.client.post(USER_GETTOKEN_URL,
                                        {
                                            "email": "invalid2@test.com",
                                            "password": "12347"
                                        })

        self.assertEqual(invalid_res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(unknown_user.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_user_token_with_valid_credentials(self):
        """ Test that a token pair is generated and returned when logging in"""

        payload = {
            "email": "joe@test.com",
            "password": "123456",
            "name": "Joe"
        }

        self.client.post(CREATE_USER_URL, payload)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertTrue(user_exists)

        token = self.client.post(USER_GETTOKEN_URL,
                                 {
                                    "email": payload['email'],
                                    "password": payload['password']
                                 })

        self.assertEqual(token.status_code, status.HTTP_200_OK)
        self.assertIn("access", token.data)
        self.assertIn("refresh", token.data)

    def test_retrieve_user_unauthorised(self):
        """ Test that authentication is required for users"""

        res = self.client.get(USER_ENDPOINT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """ Test API Requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="testpass",
            name="Joe Bloggs"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_successful(self):
        """ Test retrieving profile for logged in user"""

        res = self.client.get(USER_ENDPOINT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed(self):
        res = self.client.post(USER_ENDPOINT_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating the user profile"""
        payload = {
            "name": "new name",
            "password": "newpassword123",
            "email": "test@test.com"
        }
        res = self.client.patch(USER_ENDPOINT_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
