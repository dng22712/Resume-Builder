# ----------------- User Login Tests -----------------
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class UserLoginTests(APITestCase):
    """ Test module for user login """

    # test login with valid credentials
    def test_login_with_valid_credentials(self):
        """
        Test login with valid credentials.
        """
        # First, create a user
        user_created = get_user_model().objects.create_user(
            email='alex@yahoo.com',
            password='Powerful1!',
            first_name='John',
            last_name='Doe',
            username='alex',
            is_active=True,
            is_verified=True
        )

        url = reverse('user:token_obtain_pair')

        data = {
            'email': 'alex@yahoo.com',
            'password': 'Powerful1!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'alex@yahoo.com')
        self.assertEqual(response.data['username'], 'alex')
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
        self.assertTrue('access' in response.data)

    # test login with invalid email

    def test_login_with_invalid_email(self):
        """
        Test login with an invalid email.
        """
        url = reverse('user:token_obtain_pair')
        data = {
            'email': 'invalid_email@example',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'], ['Enter a valid email address.'])

        # test login with invalid credentials

    def test_login_with_invalid_credentials(self):  # invalid credentials
        """
        Test login with invalid credentials.
        """
        # First, create a user
        get_user_model().objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            username='johndoe'
        )

        url = reverse('user:token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'wrong_password'
        }
        response = self.client.post(url, data, format='json')

        # check if validation error is raised
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to authenticate with provided credentials')

    # test login with unregistered user
    def test_login_with_unregistered_user(self):
        """
        Test login with an unregistered user.
        """
        url = reverse('user:token_obtain_pair')
        data = {
            'email': 'alex@yahoo.com',
            'password': 'Powerful1!'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to authenticate with provided credentials')

    # test login with empty email
    def test_login_with_empty_email(self):
        """
        Test login with an empty email.
        """
        url = reverse('user:token_obtain_pair')
        data = {
            'email': '',
            'password': 'Powerful1!'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field may not be blank.')

    # test login with empty password
    def test_login_with_empty_password(self):
        """
        Test login with an empty password.
        """
        url = reverse('user:token_obtain_pair')
        data = {
            'email': 'alex@yahoo.com',
            'password': ''
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')

    # test login with unverified user
    def test_login_with_unverified_user(self):
        """
        Test login with an unverified user.
        """
        # First, create a user
        get_user_model().objects.create_user(
            email='alex@yahoo.com',
            password='Powerful1!',
            first_name='John',
            last_name='Doe',
            username='alex',
            is_active=True,
            is_verified=False
        )

        url = reverse('user:token_obtain_pair')
        data = {
            'email': 'alex@yahoo.com',
            'password': 'Powerful1!'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # test login with inactive user
    def test_login_with_inactive_user(self):
        """
        Test login with an inactive user.
        """
        # First, create a user
        get_user_model().objects.create_user(
            email='alex@yahoo.com',
            password='Powerful1!',
            first_name='John',
            last_name='Doe',
            username='alex',
            is_active=False,
            is_verified=True
        )

        url = reverse('user:token_obtain_pair')
        data = {
            'email': 'alex@yahoo.com',
            'password': 'Powerful1!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to authenticate with provided credentials')
