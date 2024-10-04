
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from rest_framework.test import APIClient
from self import self

from util.Permission.token_generator import TokenGenerator


class ForgotPasswordTestCase(TestCase):

    @classmethod
    def setUpTestData(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Powerful1!',
            first_name='John',
            last_name='Doe',
            is_active=True,
            is_verified=True,
            temporary_password_created_at=timezone.now() + timezone.timedelta(minutes=5)
            # Set expiration to 5 minutes from now
        )
        self.url = reverse('user:forgot_password')

    def test_forgot_password_valid_email(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Password reset link sent to your email')

    def test_forgot_password_invalid_email(self):
        invalid_email = {'email': 'unit_testexample.com'}
        data = {"email": invalid_email}

        with self.assertRaises(ValidationError):
            self.client.post(self.url, data=data, format="json")

    def test_forgot_password_nonexistent_user(self):
        url = reverse('user:forgot_password')
        data = {'email': 'nonexistent@example.com'}
        with self.assertRaises(get_user_model().DoesNotExist):
            self.client.post(url, data, format='json')

    def test_forgot_password_no_email(self):
        data = {'email': ''}
        with self.assertRaises(ValidationError):
            self.client.post(self.url, data, format='json')

    @patch('django.utils.timezone.now')
    @patch('django.utils.http.urlsafe_base64_encode')
    def test_forgot_password_confirm_expired_link(self, mock_urlsafe_base64_encode, mock_now):
        mock_now.return_value = timezone.datetime(2024, 3, 3, 12, 0, 0)  # mock current time
        token = TokenGenerator().make_token(str(self.user))
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse('user:forgot_password_confirm', kwargs={'uidb64': uidb64, 'token': token})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Expired link
        self.assertEqual(response.data['error'], 'Reset password link is invalid!')
