import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from user.views import ChangePasswordView


class ChangePasswordViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ChangePasswordView.as_view()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            username='johndoe',
            is_active=True,
            is_verified=True,
        )

        self.user.save()

        # Login the user and get the token

        login_data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }

        login_url = reverse('user:token_obtain_pair')
        response = self.client.post(login_url, login_data, format='json')  # login user
        self.token = response.data['access']

        # Test data

        self.valid_payload = {
            'old_password': 'Password123!',
            'new_password': 'Stringer2!',
            'confirm_password': 'Stringer2!'
        }
        self.invalid_old_password_payload = {
            'old_password': 'Passord123!',
            'new_password': 'Stringer2!',
            'confirm_password': 'Stringer2!'
        }
        self.same_password_valid_payload = {
            'old_password': 'Password123!',
            'new_password': 'Password123!',
            'confirm_password': 'Password123!'
        }
        self.password_with_personal_info_valid_payload = {
            'old_password': 'Password123!',
            'new_password': 'JohnDoe123!',
            'confirm_password': 'JohnDoe123!'
        }
        self.short_password_valid_payload = {
            'old_password': 'Password123!',
            'new_password': 'P123!',
            'confirm_password': 'P123!'
        }
        self.password_one_digit_valid_payload = {
            'old_password': 'Password123!',
            'new_password': 'Stringer!',
            'confirm_password': 'Stringer!'
        }
        self.password_one_uppercase_valid_payload = {
            'old_password': 'Password123!',
            'new_password': 'stringer1!',
            'confirm_password': 'stringer1!'
        }
        self.password_one_lowercase_valid_payload = {
            'old_password': 'Password123!',
            'new_password': 'STRINGER1!',
            'confirm_password': 'STRINGER1!'
        }
        self.password_one_special_character_valid_payload = {
            'old_password': 'Password123!',
            'new_password': 'Stringer1',
            'confirm_password': 'Stringer1'
        }

        self.change_password_url = reverse('user:change_password')

    def test_change_password_success(self):
        response = self.client.put(self.change_password_url, data=json.dumps(self.valid_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password updated successfully.')

    def test_change_password_invalid_old_password(self):
        response = self.client.put(self.change_password_url, data=json.dumps(self.invalid_old_password_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data['old_password'], 'Wrong password.')

    def test_change_password_same_as_old_password(self):
        response = self.client.put(self.change_password_url, data=json.dumps(self.same_password_valid_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'], 'New password cannot be the same as old password.')

    def test_change_password_contains_personal_info(self):
        response = self.client.put(self.change_password_url,
                                   data=json.dumps(self.password_with_personal_info_valid_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'], 'New password cannot contain personal information.')

    def test_change_password_short_password(self):
        response = self.client.put(self.change_password_url,
                                   data=json.dumps(self.short_password_valid_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'], 'New password must be at least 6 characters.')

    def test_change_password_complexity_validation_one_digit(self):
        response = self.client.put(self.change_password_url,
                                   data=json.dumps(self.password_one_digit_valid_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'],
                         'Password must contain at least one number')

    def test_change_password_complexity_validation_one_uppercase(self):
        response = self.client.put(self.change_password_url,
                                   data=json.dumps(self.password_one_uppercase_valid_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'],
                         'Password must contain at least one uppercase letter')

    def test_change_password_complexity_validation_one_lowercase(self):
        response = self.client.put(self.change_password_url,
                                   data=json.dumps(self.password_one_lowercase_valid_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'],
                         'Password must contain at least one lowercase letter')

    def test_change_password_complexity_validation_one_special_character(self):
        response = self.client.put(self.change_password_url,
                                   data=json.dumps(self.password_one_special_character_valid_payload),
                                   content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.token)

        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['new_password'], 'Password must contain at least one special character')
