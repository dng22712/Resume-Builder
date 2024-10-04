from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class UserProfileByUserNameTest(APITestCase):
    def setUp(self):
        url = reverse('user:register')
        data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        }

        response = self.client.post(url, data, format='json')

    def test_get_user_profile_by_username_success(self):
        """
        `GET /api/v1/user/profile/{username}/` should return the useprofile
        """

        url = reverse('user_profile:profile-by-username', kwargs={'username': 'johndoe'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_user_profile_by_username_not_found(self):
        """
        Test retrieving a user profile by username when it doesn't exist.
        """

        url = reverse('user_profile:profile-by-username', kwargs={'username': 'unknown_user'})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 404)
