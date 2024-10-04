from unittest.mock import patch

from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse


from user.views import FacebookLogin


# ----------------- User Registration Tests -----------------

class UserRegistrationTests(APITestCase):
    def test_user_registration_with_valid_credentials(self):
        """
        Test user registration with a valid email.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(get_user_model().objects.get().email, 'test@example.com')
        self.assertEqual(get_user_model().objects.get().first_name, 'John')
        self.assertEqual(get_user_model().objects.get().last_name, 'Doe')
        self.assertEqual(get_user_model().objects.get().username, 'johndoe')

    # user registration with invalid email
    def test_user_registration_with_invalid_email(self):
        """
        Test user registration with an invalid email.
        """
        url = reverse('user:register')
        data = {
            'email': 'invalid_email',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

    # user registration with password less than 6 characters
    def test_user_registration_with_password_less_than_6_characters(self):
        """
        Test user registration with a password less than 6 characters.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'Sti1!',
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        }
        response = self.client.post(url, data, format='json')
        # check if validation error is raised
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'Ensure this field has at least 6 characters.')

    # verify error when test user registration when email is same as password
    def test_user_registration_when_email_is_same_as_password(self):
        """
        Test user registration with an email that is the same as the password.
        """
        url = reverse('user:register')
        data = {
            'email': 'Password123!@example.com',
            'password': 'Password123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must not contain email')

    # verify error when test user registration when username is same as password
    def test_user_registration_when_username_is_same_as_password(self):
        """
        Test user registration with a username that is the same as the password.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'Johndoe1!',
            'first_name': 'Alex',
            'last_name': 'taker',
            'username': 'Johndoe1'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must not contain username')

    # verify error when test user registration when first name is same as password
    def test_user_registration_when_first_name_is_same_as_password(self):
        """
        Test user registration with a first name that is the same as the password.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'Johndoe1!',
            'first_name': 'Johndoe1',
            'last_name': 'taker',
            'username': 'Alex'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must not contain first name')

    # verify error when test user registration when last name is same as password
    def test_user_registration_when_last_name_is_same_as_password(self):
        """
        Test user registration with a last name that is the same as the password.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'Johndoe1!',
            'first_name': 'Alex',
            'last_name': 'Johndoe1',
            'username': 'taker'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must not contain last name')

    # verify error when test user registration when password does not contain uppercase letter
    def test_user_registration_when_password_does_not_contain_uppercase_letter(self):
        """
        Test user registration with a password that does not contain an uppercase letter.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'johndoe1!',
            'first_name': 'Alex',
            'last_name': 'taker',
            'username': 'johndoe'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must contain at least one uppercase letter')

    # verify error when test user registration when password does not contain lowercase letter
    def test_user_registration_when_password_does_not_contain_lowercase_letter(self):
        """
        Test user registration with a password that does not contain a lowercase letter.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'JOHNDOE1!',
            'first_name': 'Alex',
            'last_name': 'taker',
            'username': 'johndoe'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must contain at least one lowercase letter')

    # verify error when test user registration when password does not contain number
    def test_user_registration_when_password_does_not_contain_number(self):
        """
        Test user registration with a password that does not contain a number.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'JohnDoe!',
            'first_name': 'Alex',
            'last_name': 'taker',
            'username': 'johndoe'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must contain at least one number')

    # verify error when test user registration when password does not contain special character
    def test_user_registration_when_password_does_not_contain_special_character(self):
        """
        Test user registration with a password that does not contain a special character.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'JohnDoe1',
            'first_name': 'Alex',
            'last_name': 'taker',
            'username': 'johndoe'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must contain at least one special character')

    # verify error when test user registration when username contains special character
    def test_user_registration_when_username_contains_special_character(self):
        """
        Test user registration with a username that contains a special character.
        """
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'JohnDoe1!',
            'first_name': 'Alex',
            'last_name': 'taker',
            'username': 'johndoe!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Username must not contain special characters')






