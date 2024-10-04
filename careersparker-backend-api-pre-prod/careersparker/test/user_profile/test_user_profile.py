from datetime import datetime

from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.core.files import File
from django.conf import settings
from unittest.mock import patch

from user import models
from user.models import User
from util.signal_notifier.signal import create_user_profile


class UserProfileTest(APITestCase):

    def test_user_profile_created_after_registration(self):
        """
        Test user profile is created after user registration.
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

        user = get_user_model().objects.get()

        # assert the user profile is created
        self.assertTrue(models.Profile.objects.filter(user=user).exists())
        self.assertTrue(models.Profile.objects.get(user=user).user == user)
        self.assertTrue(models.Profile.objects.get(user=user).user.email == 'test@example.com')
        self.assertTrue(models.Profile.objects.get(user=user).user.first_name == 'John')
        self.assertTrue(models.Profile.objects.get(user=user).user.last_name == 'Doe')
        self.assertTrue(models.Profile.objects.get(user=user).user.username == 'johndoe')

    def test_user_profile_image_created_after_registration(self):
        """
        Test user profile image is created after user registration.
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

        user = get_user_model().objects.get()

        # assert the user profile image is created
        self.assertTrue(models.ProfilePicture.objects.filter(user=user).exists())
        self.assertTrue(models.ProfilePicture.objects.get(user=user).user == user)
        self.assertTrue(models.ProfilePicture.objects.get(user=user).user.email == 'test@example.com')
        self.assertTrue(models.ProfilePicture.objects.get(user=user).user.first_name == 'John')
        self.assertTrue(models.ProfilePicture.objects.get(user=user).user.last_name == 'Doe')
        self.assertTrue(models.ProfilePicture.objects.get(user=user).user.username == 'johndoe')

    # test user profile is not created if user registration fails
    def test_user_profile_not_created_if_registration_fails(self):
        """
            Test user profile is not created if user registration fails.
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

        if response.status_code == status.HTTP_201_CREATED:
            user = get_user_model().objects.get()
            self.assertFalse(models.Profile.objects.filter(user=user).exists())
            self.assertFalse(models.Profile.objects.filter(user=user).exists())


# ---------------------- Update User Profile Tests ----------------------
class UpdateUserProfileTest(APITestCase):
    def setUp(self):
        self.register_url = reverse('user:register')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        }
        self.response = self.client.post(self.register_url, self.user_data, format='json')

    def test_update_own_profile(self):
        """
        Test updating own profile.
        """
        user = get_user_model().objects.get()
        profile = models.Profile.objects.get(user=user)
        url = reverse('user_profile:profile-update', kwargs={'pk': profile.pk})
        self.client.force_authenticate(user=user)

        data = {
            'title_before': 'Updated Title Before',
            'title_after': 'Updated Title After',
            'about': 'Updated about',
            'phone_number': '08012345678',
            'date_of_birth': '1990-01-01',
            'nationality': 'Nigerian',
            'street_address': 'Updated Street Address',
            'city': 'Updated City',
            'state': 'Updated State',
            'country': 'Updated Country',
            'postal_code': '12345',
            'website': 'https://example.com',
            'linkedin': 'https://linkedin.com',
            'last_name': 'Doe',
            'first_name': 'John',
            'username': 'johndoe'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertEqual(profile.title_before, 'Updated Title Before')
        self.assertEqual(profile.title_after, 'Updated Title After')
        self.assertEqual(profile.about, 'Updated about')
        self.assertEqual(profile.phone_number, '08012345678')
        self.assertEqual(profile.date_of_birth,
                         datetime.strptime('1990-01-01', '%Y-%m-%d').date())  # Convert string to date

        self.assertEqual(profile.nationality, 'Nigerian')
        self.assertEqual(profile.street_address, 'Updated Street Address')
        self.assertEqual(profile.city, 'Updated City')
        self.assertEqual(profile.state, 'Updated State')
        self.assertEqual(profile.country, 'Updated Country')
        self.assertEqual(profile.postal_code, '12345')
        self.assertEqual(profile.website, 'https://example.com')
        self.assertEqual(profile.linkedin, 'https://linkedin.com')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.username, 'johndoe')

        # update the user profile again
        data = {
            'title_before': 'Updated Title Before 2',
            'title_after': 'Updated Title After 2',
            'about': 'Updated about 2',
            'phone_number': '08012345679',
            'date_of_birth': '1990-01-02',
            'nationality': 'Nigerian 2',
            'street_address': 'Updated Street Address 2',
            'city': 'Updated City 2',
            'state': 'Updated State 2',
            'country': 'Updated Country 2',
            'postal_code': '12346',
            'website': 'https://example2.com',
            'linkedin': 'https://linkedin2.com',
            'last_name': 'Doe 2',
            'first_name': 'John 2',
            'username': 'johndoe2'
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertEqual(profile.title_before, 'Updated Title Before 2')
        self.assertEqual(profile.title_after, 'Updated Title After 2')
        self.assertEqual(profile.about, 'Updated about 2')
        self.assertEqual(profile.phone_number, '08012345679')
        self.assertEqual(profile.date_of_birth, datetime.strptime('1990-01-02', '%Y-%m-%d').date())
        self.assertEqual(profile.nationality, 'Nigerian 2')
        self.assertEqual(profile.street_address, 'Updated Street Address 2')
        self.assertEqual(profile.city, 'Updated City 2')
        self.assertEqual(profile.state, 'Updated State 2')
        self.assertEqual(profile.country, 'Updated Country 2')
        self.assertEqual(profile.postal_code, '12346')
        self.assertEqual(profile.website, 'https://example2.com')
        self.assertEqual(profile.linkedin, 'https://linkedin2.com')
        self.assertEqual(user.last_name, 'Doe 2')
        self.assertEqual(user.first_name, 'John 2')
        self.assertEqual(user.username, 'johndoe2')

    def test_update_another_user_profile(self):
        """

        :return:
        """
        # Create another user
        other_user_data = {
            'email': 'other@example.com',
            'password': 'Password123!',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'username': 'janesmith'
        }
        self.client.post(self.register_url, other_user_data, format='json')
        other_user = get_user_model().objects.get(email='other@example.com')
        user = get_user_model().objects.get(email='test@example.com')

        # Fetch profile of the first user
        profile = models.Profile.objects.get(user=user)
        url = reverse('user_profile:profile-update', kwargs={'pk': profile.pk})

        # Authenticate as the other user
        self.client.force_authenticate(user=other_user)

        # Attempt to update the profile
        data = {
            'title_before': 'Updated Title Before',
            'title_after': 'Updated Title After',
            'about': 'Updated about',
            'phone_number': '08012345678',
            'date_of_birth': '1990-01-01',
            'nationality': 'Nigerian',
            'street_address': 'Updated Street Address',
            'city': 'Updated City',
            'state': 'Updated State',
            'country': 'Updated Country',
            'postal_code': '12345',
            'website': 'https://example.com',
            'linkedin': 'https://linkedin.com',
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'You are not authorized to update this profile.')
