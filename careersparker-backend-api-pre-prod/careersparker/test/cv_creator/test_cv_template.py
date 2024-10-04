from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.reverse import reverse

from cvbuilder.models import CvTemplate
from fixed_payments.models import StripeFixedPayment


# ----------------------------------------------------------------
# Create Cv template for CV
# ----------------------------------------------------------------
class CvTemplateCreation(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            username='johndoe',
            is_active=True,
            is_verified=True,
        )

        self.user.save()  # create a user

        login_url = reverse('user:token_obtain_pair')

        token_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
        }

        response = self.client.post(login_url, token_data, format='json')  # login user
        self.token = response.data['access']  # get token

        # create a CV
        url = reverse('cvbuilder:cvbuilder-list')
        payment_data = {
            'user': self.user,
            'stripe_session_id': 'test_session_id',
            'stripe_customer_id': 'test_customer_id',
            'stripe_payment_intent_id': 'test_payment_intent_id',
            'stripe_payment_link_id': 'test_payment_link_id',
            'stripe_customer_email': 'test@example.com',
            'stripe_payment_status': 'test_payment_status',
            'stripe_status': 'test_status'
        }
        payment = StripeFixedPayment.objects.create(**payment_data)  # create a payment
        payment.save()

        data = {
            'user': self.user.id,
            'cv_title': 'Test CV',
            'cv_slug': 'test-cv',
        }

        response = self.client.post(url, data, format='json, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 201)

        # create a CV template

    def test_create_cv_template_fixed_payment_success(self):
        url = reverse('cv_template:template_by_cv_id', args=[1])
        with open('careersparker/static/public/user_profile_image.png', 'rb') as f:
            image_content = f.read()
        data = {
            'cv': 1,
            'user': self.user.id,
            'cv_template_name': 'Test Template',
            'cv_template_profession': 'Test Profession',
            'cv_template_thumbnail': SimpleUploadedFile('user_profile_image.png', image_content),
            'cv_template_thumbnail_small': SimpleUploadedFile('user_profile_image.png', image_content),
        }
        self.user.cv_template_count = 1  # set cv template count to 1
        self.user.save()
        response = self.client.post(url, data, format='multipart, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['cv_template_name'], 'Test Template')
        self.assertTrue(response.data['cv_template_profession'], 'Test Profession')
        self.assertTrue(response.data['cv_template_thumbnail'], 'user_profile_image.png')
        self.assertTrue(response.data['cv_template_thumbnail_small'], 'user_profile_image.png')
        self.assertTrue(
            CvTemplate.objects.filter(cv_template_name='Test Template', cv_template_profession='Test Profession',
                                      cv_template_thumbnail='user-media/user-profile/cv-template/user_profile_image.png',
                                      cv_template_thumbnail_small='user-media/user-profile/cv-template/user_profile_image.png').exists())

    def test_create_cv_template_is_set_to_default_when_user_is_free(self):
        url = reverse('cv_template:template_by_cv_id', args=[1])
        with open('careersparker/static/public/user_profile_image.png', 'rb') as f:
            image_content = f.read()
        data = {
            'cv': 1,
            'user': self.user.id,
            'cv_template_name': 'Test Template',
            'cv_template_profession': 'Test Profession',
            'cv_template_thumbnail': SimpleUploadedFile('user_profile_image.png', image_content),
            'cv_template_thumbnail_small': SimpleUploadedFile('user_profile_image.png', image_content),
        }

        response = self.client.post(url, data, format='multipart, content_type=application/json',
                                    HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['cv_template_name'], 'Test Template')
        self.assertTrue(response.data['cv_template_profession'], 'Test Profession')
        self.assertTrue(response.data['cv_template_thumbnail'], 'user_profile_image.png')
        self.assertTrue(response.data['cv_template_thumbnail_small'], 'user_profile_image.png')
        self.assertTrue(CvTemplate.objects.filter(cv_template_name='default', cv_template_profession='Test Profession',
                                                  cv_template_thumbnail='user-media/user-profile/cv-template/user_profile_image.png',
                                                  cv_template_thumbnail_small='user-media/user-profile/cv-template/user_profile_image.png').exists())

    # def test_update_cv_template_with_fixed_payment(self):
    #     url = reverse('cv_template:template_by_cv_id', args=[1])
    #     with open('careersparker/static/public/user_profile_image.png', 'rb') as f:
    #         image_content = f.read()
    #     data = {
    #         'cv': 1,
    #         'user': self.user.id,
    #         'cv_template_name': 'Test Template',
    #         'cv_template_profession': 'Test Profession',
    #         'cv_template_thumbnail': SimpleUploadedFile('user_profile_image.png', image_content),
    #         'cv_template_thumbnail_small': SimpleUploadedFile('user_profile_image.png', image_content),
    #     }
    #     self.user.cv_template_count = 1
    #     self.user.save()
    #
    #     response = self.client.post(url, data, format='multipart, content_type=application/json',
    #                                 HTTP_AUTHORIZATION=f'Bearer {self.token}')
    #     print("HERE", response.data)
    #
    #     self.assertEqual(response.status_code, 201)
    #
    #     self.assertTrue(response.data['cv_template_name'], 'Test Template')
    #
    #     with open('careersparker/static/public/user_profile_image.png', 'rb') as f:
    #         image_content = f.read()
    #
    #     data_update = {
    #         'cv': 1,
    #         'user': self.user.id,
    #         'cv_template_name': 'Updated Template',
    #         'cv_template_profession': 'Updated Profession',
    #         # 'cv_template_thumbnail': SimpleUploadedFile('user_profile_image.png', image_content),
    #         # 'cv_template_thumbnail_small': SimpleUploadedFile('user_profile_image.png', image_content),
    #     }
    #
    #     self.user.cv_template_count = 1
    #     self.user.save()
    #
    #     url = reverse('cv_template:template_by_id', args=[1])
    #
    #     responses = self.client.patch(url, data_update, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.token}')
    #
    #
    #
    #     print(responses.data)
    #
    #     self.assertEqual(response.status_code, 200)


