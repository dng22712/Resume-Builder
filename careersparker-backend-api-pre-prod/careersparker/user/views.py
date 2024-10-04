import os
import random
import string

import pytz
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import BadHeaderError
from django.core.validators import EmailValidator
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import make_naive
from drf_spectacular.utils import extend_schema, OpenApiParameter
from jwt.utils import force_bytes
from rest_framework import generics, status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from user import serializers
from user.serializers import UserSerializer, AuthTokenSerializer
from util.Permission.token_generator import TokenGenerator

from util.general.send_email import send_forgot_password_email
from util.signal_notifier.signal import user_login
from util.user.social_user_auth import get_user_details_from_facebook, get_user_details_from_linkedin, \
    get_user_details_from_google
from util.user.user_validator import validate_new_password


@extend_schema(tags=["User"], description="API endpoint for registering new users.")
class CreateUserView(generics.CreateAPIView):
    """
    ***Creates a new user.***

    This view allows authorized users to register new accounts in the system.
    The submitted data must be valid according to the `UserSerializer` schema.

    **Request:**

    - **Method:** POST
    - **Content-Type:** application/json
    - **Body:**

      ```json
      {
          "username": "string",
          # Other fields as defined in the UserSerializer
      }
      ```

    **Response:**

    - **Status:**
      - 201 Created: Upon successful user creation.
      - 400 Bad Request: If validation fails or other errors occur.

    **Example Response:**

    ```json
    {
        "id": 1,
        "username": "new_user",
        # Other fields returned by the UserSerializer
    }
    ```

    **Permissions:**

    - Required: User must be authenticated.
    - Additional permission checks may be defined in the view or serializer.

    **Notes:**

    - Password and other sensitive fields should be handled securely by the serializer.
    - Consider using a password hashing mechanism instead of storing passwords in plain text.

    """
    serializer_class = UserSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new user.

        - Validates the request data using the `UserSerializer`.
        - Creates a new user instance if validation is successful.
        - Returns a 201 Created response with the user details.
        - Returns a 400 Bad Request response with validation errors.

        **Raises:**

        - ValidationError: If data is invalid.
        - Other exceptions as necessary.

        """

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["User"])
class CreateTokenView(ObtainAuthToken):
    """
    ***API endpoint for obtaining registration_authentication tokens.***

    This view allows users to generate access and refresh tokens for registration_authentication.
    It inherits from `ObtainAuthToken` class provided by Django REST framework.

    **Permissions:**

    * This view doesn't require any specific permissions.

    **Response:**

    * On successful registration_authentication, returns a JSON response containing:
        * `user_id`: An integer representing the user's ID.
        * `email`: The user's email address.
        * `username`: The user's username.
        * `first_name`: The user's first name.
        * `last_name`: The user's last name.
        * `access`: The access token string.

    **Error handling:**

    * If the user is not verified or not active, returns a 400 Bad Request response with an 'error' key and a message.

    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        **Handles POST requests for token generation.**

        This method:

        1. Validates the request data using the `AuthTokenSerializer`.
        2. Retrieves the authenticated user from the serializer data.
        3. Checks if the user is verified and active.
        4. Generates refresh and access tokens if the user is valid.
        5. Returns a JSON response with user information and access token.

        **Raises:**

        * `ValidationError` if the request data is invalid.

        **Returns:**

        * A JSON response with user information and access token on success.
        * A 400 Bad Request response with an 'error' key and message if the user is not verified or not active.

        """

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)  # generate refresh token
        access = str(refresh.access_token)
        email = user.email
        username = user.username
        first_name = user.first_name
        last_name = user.last_name
        if access:
            user_login(request, user)

        return Response({
            'user_id': user.pk,
            'email': email,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'access': access,
        })


@extend_schema(tags=["User"])
class RefreshTokenView(generics.GenericAPIView):
    """
    API endpoint for refreshing access tokens for authenticated users.

    This view is responsible for refreshing access tokens for users who have already authenticated using the login endpoint. It accepts a refresh token in the request body and returns a new access token if the refresh token is valid.

    **Permissions:**
    - IsAuthenticated: Required for all requests.

    **Request:**
    - **POST**:
        - **Body:**
            - `refresh` (str): The refresh token to be used for generating a new access token.

    **Response:**
    - **200 OK:**
        - **Body:**
            - `access` (str): The new access token.

    **Errors:**
    - **400 Bad Request:** If the request data is invalid.
    - **401 Unauthorized:** If the refresh token is invalid or expired.
    - **404 Not Found:** If the user associated with the refresh token is not found.
    """

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    @staticmethod
    @transaction.atomic
    def post(request, *args, **kwargs):
        """
        **Handles POST requests to refresh a user's access token.**

        - Retrieves the refresh token from the request body.
        - Decodes the refresh token to obtain the user ID.
        - Retrieves the user object associated with the user ID.
        - Generates a new access token for the user.
        - Returns a JSON response containing the new access token.

        *Raises:*

        - APIException: If the refresh token is invalid or missing, or if the user
                does not have the "refresh_tokens" permission.
        """

        refresh_token = request.data.get('refresh')  # get refresh token
        decoded_token = AccessToken(refresh_token)  # decode token
        user_id = decoded_token['user_id']
        user = User.objects.get(id=user_id)  # get user
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        return Response({'access': access})


@extend_schema(tags=["User"], description="API endpoint for verifying user accounts using email confirmation tokens.")
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    **API endpoint for managing the currently authenticated user's profile information.**

    *Permissions:*
    - Must be authenticated with a JWT token.

    *Attributes:*
        serializer_class (UserSerializer): Serializer class for user data.
        authentication_classes (list): List of registration_authentication classes, currently JWTAuthentication.
        parser_classes (tuple): List of parsers supported, including MultiPartParser, FormParser, and JSONParser.
        permission_classes (list): List of permission classes, currently IsAuthenticated.

    *Methods:*
        get_object(self): Retrieves the currently authenticated user object.

    *Returns:*
        UserSerializer instance representing the user's profile data on successful GET request.
        Appropriate error response on unsuccessful requests.
    """
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]  # user JWT for registration_authentication
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        **Retrieves the currently authenticated user object.**

        *Returns:*

        -   User object representing the currently authenticated user.
        """

        return self.request.user


# Connect to Facebook using social auth
@extend_schema(tags=["User"], description="API view for Facebook login.")
class FacebookLogin(APIView):
    """
    **API view for Facebook login.**

    This view allows users to login using their Facebook credentials.

    It takes an access token as a query parameter and performs the following steps:

    1. Validates the access token using the provided serializer.
    2. Retrieves user details from Facebook using the access token.
    3. Checks if the user exists in the database.
    4. If the user exists:

    - Verifies the user if not already verified and active.
    - Returns a response containing user information and an access token.

    5. If the user does not exist:

    - Creates a new user with the retrieved details.
    - Verifies the newly created user.
    - Returns a response containing user information and an access token.

    ***Parameters:***

    request (Request): The incoming request object.

    ***Returns:***

    Response: A JSON response containing user information and an access token on success,
              or an error message on failure.

    """
    serializer_class = serializers.FacebookLoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        """
        This view handles POST requests for Facebook login.

        **Expected request data:**

        * `fb_access_token`: A valid Facebook access token.

        **Response:**

        * Upon successful login:
            * `user_id`: User's primary key.
            * `email`: User's email address.
            * `username`: User's username.
            * `first_name`: User's first name (if provided by Facebook).
            * `last_name`: User's last name (if provided by Facebook).
            * `access`: A valid access token for the user.
        * Upon error:
            * `error`: A string describing the error.

        **Functionality:**

        1. Validates the provided `fb_access_token`.
        2. Attempts to retrieve user details from Facebook using the access token.
        3. If the user already exists in the database:
            * Verifies and activates the user if necessary.
            * Responds with user information and an access token.
        4. If the user doesn't exist:
            * Creates a new user with information obtained from Facebook.
            * Responds with user information and an access token.

        **Error handling:**

        * `ValidationError`: Raised for invalid access tokens or missing data in Facebook response.
        * `User.DoesNotExist`: Raised if the user is not found in the database.

        **Notes:**

        * This view assumes the existence of functions like `get_user_details_from_facebook`
          and the `RefreshToken` model for access token management.

        """

        serializer = self.serializers_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data['fb_access_token']

        try:
            user_details = get_user_details_from_facebook(access_token)  # get user details from Facebook

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:

            user = get_user_model().objects.get(email=user_details['email'])  # check if user exists in the database
            print(user)

            if user:
                # The user exists in the database and is active, return a token
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                # verify the user if user is not verified
                if not user.is_verified or not user.is_active:  # verify the user if user is not verified
                    user.is_verified = True
                    user.is_active = True
                    user.save()

                return Response({
                    'user_id': user.pk,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'access': access,
                })

        except User.DoesNotExist:
            # The user does not exist in the database, create a new user
            new_user = User.objects.create_user(
                username=user_details['username'],
                email=user_details['email'],
                first_name=user_details['first_name'],
                last_name=user_details['last_name'],
                is_verified=True,
                is_active=True
            )
            refresh = RefreshToken.for_user(new_user)
            access = str(refresh.access_token)
            return Response({
                'user_id': new_user.pk,
                'email': new_user.email,
                'username': new_user.username,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'access': access,
            })


# LinkedIn
@extend_schema(tags=["User"], description="API endpoint for logging in users using their LinkedIn credentials.")
class LinkedInLogin(APIView):
    """
    **API endpoint for logging in users using their LinkedIn credentials.**

    This view expects an access token obtained from LinkedIn in the request query parameters.
    It validates the token, retrieves user details from LinkedIn, and checks if the user exists in the database.

    If the user exists:

    - Verifies the user if not already verified and active.
    - Generates a new access token and returns user details.

    If the user doesn't exist:

    - Creates a new user with the retrieved details and sets them as verified and active.
    - Generates a new access token and returns user details.

    Raises a 400 Bad Request error if the access token is invalid or any other validation error occurs.

    """
    serializer_class = serializers.LinkedInLoginSerializer  # serializer class for LinkedIn login
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        """
        This view handles POST requests for LinkedIn login.

    **Expected request data:**

    * `li_access_token`: A valid LinkedIn access token.

    **Response:**

    * Upon successful login:
        * `user_id`: User's primary key.
        * `email`: User's email address.
        * `username`: User's username.
        * `first_name`: User's first name (if provided by LinkedIn).
        * `last_name`: User's last name (if provided by LinkedIn).
        * `access`: A valid access token for the user.
    * Upon error:
        * `error`: A string describing the error.

    **Functionality:**

    1. Validates the provided `fb_access_token`.
    2. Attempts to retrieve user details from LinkedIn using the access token.
    3. If the user already exists in the database:
        * Verifies and activates the user if necessary.
        * Responds with user information and an access token.
    4. If the user doesn't exist:
        * Creates a new user with information obtained from LinkedIn.
        * Responds with user information and an access token.

    **Error handling:**

    * `ValidationError`: Raised for invalid access tokens or missing data in LinkedIn response.
    * `User.DoesNotExist`: Raised if the user is not found in the database.

    **Notes:**

    * This view assumes the existence of functions like `get_user_details_from_linkedin`
      and the `RefreshToken` model for access token management.


        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data['li_access_token']

        try:
            user_details = get_user_details_from_linkedin(access_token)  # get user details from LinkedIn

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:

            user = User.objects.get(email=user_details['email'])  # check if user exists in the database

            if user:
                # The user exists in the database and is active, return a token
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                # verify the user if user is not verified
                if not user.is_verified or not user.is_active:  # verify the user if user is not verified
                    user.is_verified = True
                    user.is_active = True
                    user.save()

                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                return Response({
                    'user_id': user.pk,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'access': access,
                })

            else:
                return Response({'error': 'User is not active'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # The user does not exist in the database, create a new user
            new_user = User.objects.create_user(
                username=user_details['username'],
                email=user_details['email'],
                first_name=user_details['first_name'],
                last_name=user_details['last_name'],
                is_verified=True,
                is_active=True
            )

            refresh = RefreshToken.for_user(new_user)
            access = str(refresh.access_token)
            return Response({
                'user_id': new_user.pk,
                'email': new_user.email,
                'username': new_user.username,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'access': access,
            })


# Google
@extend_schema(tags=["User"], description="API endpoint for logging in users using their Google credentials.")
class GoogleLogin(APIView):
    """
    **API endpoint for logging in users using their Google credentials.**

        This view expects an access token obtained from Google in the request query parameters.
        It validates the token, retrieves user details from Google, and checks if the user exists in the database.

        If the user exists:

        - Verifies the user if not already verified and active.
        - Generates a new access token and returns user details.

        If the user doesn't exist:

        - Creates a new user with the retrieved details and sets them as verified and active.
        - Generates a new access token and returns user details.

        Raises a 400 Bad Request error if the access token is invalid or any other validation error occurs.
    """
    serializer_class = serializers.GoogleLoginSerializer  # serializer class for Google login
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        """
        This view handles POST requests for Google login.

        **Expected request data:**

        * `fb_access_token`: A valid Google access token.

        **Response:**

        * Upon successful login:
            * `user_id`: User's primary key.
            * `email`: User's email address.
            * `username`: User's username.
            * `first_name`: User's first name (if provided by Google).
            * `last_name`: User's last name (if provided by Google).
            * `access`: A valid access token for the user.
        * Upon error:
            * `error`: A string describing the error.

        **Functionality:**

        1. Validates the provided `gg_access_token`.
        2. Attempts to retrieve user details from Google using the access token.
        3. If the user already exists in the database:
            * Verifies and activates the user if necessary.
            * Responds with user information and an access token.
        4. If the user doesn't exist:
            * Creates a new user with information obtained from Google.
            * Responds with user information and an access token.

        **Error handling:**

        * `ValidationError`: Raised for invalid access tokens or missing data in Google response.
        * `User.DoesNotExist`: Raised if the user is not found in the database.

        **Notes:**

        * This view assumes the existence of functions like `get_user_details_from_google`
          and the `RefreshToken` model for access token management.

        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data['g_access_token']

        try:
            user_details = get_user_details_from_google(access_token)  # get user details from Google

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:

            user = User.objects.get(email=user_details['email'])  # check if user exists in the database

            if user:
                # The user exists in the database and is active, return a token
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                # verify the user if user is not verified
                if not user.is_verified or not user.is_active:  # verify the user if user is not verified
                    user.is_verified = True
                    user.is_active = True
                    user.save()

                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                return Response({
                    'user_id': user.pk,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'access': access,
                })

            else:
                return Response({'error': 'User is not active'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # The user does not exist in the database, create a new user
            new_user = User.objects.create_user(
                username=user_details['username'],
                email=user_details['email'],
                first_name=user_details['first_name'],
                last_name=user_details['last_name'],
                is_verified=True,
                is_active=True
            )

            refresh = RefreshToken.for_user(new_user)
            access = str(refresh.access_token)
            return Response({
                'user_id': new_user.pk,
                'email': new_user.email,
                'username': new_user.username,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'access': access,
            })


@extend_schema(tags=["User"], description="API endpoint for changing the password of the currently authenticated user.")
class ChangePasswordView(generics.UpdateAPIView):
    """
    **API endpoint for changing the password of the currently authenticated user.**

    *Permissions:*

    - Must be authenticated with a JWT token.

    *Attributes:*

    - serializer_class (ChangePasswordSerializer): Serializer class for password change data.
    - authentication_classes (list): List of registration_authentication classes, currently JWTAuthentication.
    - permission_classes (list): List of permission classes, currently IsAuthenticated.
    - MIN_PASSWORD_LENGTH (int): Minimum allowed password length (default 6).

    **Methods:**

    *put(self, request, args, kwargs):*

    - Updates the user's password.

    **Returns:**

    Appropriate response based on the password change operation:

    - Success message on successful password update.
    - Error message indicating the reason for failure.

    """
    serializer_class = serializers.ChangePasswordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    MIN_PASSWORD_LENGTH = 6

    def get_object(self):
        """Retrieve and return authentication user"""

        return self.request.user

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """
        **Updates the password of the currently authenticated user.**

        Performs the following checks before updating the password:

        - Old password matches the provided one.
        - New password is different from the old password.
        - New password does not contain user's personal information.
        - New password meets the minimum length requirement.
        - New password passes complexity validation.

        On successful update, returns a success message. Otherwise, returns an error message indicating the reason for failure.

        *Args:*

        -   request (Request): Incoming request object.

        *Returns:*

        - Response object with appropriate message or error details.
        """

        user = self.request.user
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not obj.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)

        # make sure the new password is not the same as the old password
        # get the new password from the serializer

        new_password = serializer.data.get('new_password')
        old_password = serializer.data.get('old_password')

        # new_password = serializer.data.get['new_password']

        if new_password == old_password:
            return Response(
                {'new_password': 'New password cannot be the same as old password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # make sure the new password does not contain the personal information of the user

        personal_info = [user.username.lower(), user.email.lower(), user.first_name.lower(), user.last_name.lower()]

        if new_password.lower() in personal_info:
            return Response(
                {'new_password': 'New password cannot contain personal information.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Give error if the new password contains 4 consecutive characters of the user's personal information
        for i in range(len(new_password) - 3):
            if new_password[i:i + 4].lower() in personal_info:
                return Response(
                    {'new_password': 'New password cannot contain personal information.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # make sure the new password meets the minimum length requirement (6 characters)
        if len(new_password) < self.MIN_PASSWORD_LENGTH:
            return Response(
                {'new_password': 'New password must be at least 6 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # validate password complexity
        try:
            validate_new_password(new_password)
        except ValueError as e:
            return Response({'new_password': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# forgot password via email
@extend_schema(tags=["User"], description="API endpoint for initiating the password reset process.")
class ForgotPassword(GenericAPIView):
    """
    ***Initiates the password reset process by sending a password reset link to the user's email.***

    ***Attributes:***

    - authentication_classes (list): List of registration_authentication classes used for this view (empty in this case).
    - permission_classes (list): List of permission classes used for this view (empty in this case).
    - serializer_class (ForgotPasswordSerializer): The serializer class used to validate the request data.

    ***Methods:***

    *post(self, request, args, kwargs):*

    -   Takes a POST request with the user's email in the request body.

    ***Raises:***

    - ValidationError: If the email format is invalid.
    - User.DoesNotExist: If no user is found with the provided email.
    - BadHeaderError: If the password reset email cannot be sent.
    - Exception: If any other error occurs during the process.

    ***Returns:***

    - 200 OK with a success message if the email is sent.
    - 400 Bad Request with an error message if the email is not sent.

    ***Notes:***

    - This view uses transactions to ensure data consistency.
    - The 'USER_PASSWORD_RESET_URL' environment variable must be set with the password reset URL template.
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = serializers.ForgotPasswordSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Initiates a password reset for a user.

        This endpoint accepts a POST request with the following data:

        - `email`: (required) The email address of the user requesting the password reset.

        Upon successful validation, the endpoint performs the following actions:

        1. Validates the provided email address format.
        2. Retrieves the user object associated with the email address.
        3. Generates a unique password reset token.
        4. Creates a temporary password for the user.
        5. Sets an expiration time for the temporary password (15 minutes).
        6. Sends a password reset email to the user with a link containing the token and temporary password.

        Returns:

        - A JSON response with the following status codes:
            - 200 OK: Password reset link sent successfully.
            - 400 BAD REQUEST:
                - Invalid email format.
                - Email address not found in the system.
                - Error sending password reset email.
            - 404 NOT FOUND: User with the provided email does not exist.

        Raises:

        - ValidationError: If the email address format is invalid.
        - User.DoesNotExist: If the user with the provided email does not exist.
        - Exception: Any other unexpected error during the process.



        """
        email = request.data.get('email', None)
        if email is None:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            EmailValidator()(email)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # check if user exist
            user = get_user_model().objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        name = user.first_name or user.last_name or user.username

        # generate token and send email to user
        token = TokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(str(user.pk)))

        user_password_reset_url = os.getenv('USER_PASSWORD_RESET_URL')
        reset_account_url = user_password_reset_url + '/forgot_password_confirm/' + uid + '/' + token

        # temporary_password = user.objects.make_random_password()

        # generate alphanumeric password with one special character and one digit and Uppercase letter (12-16 characters)
        temporary_password = ''.join(
            random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation, k=16))

        # generate temporary password reset link and set expiration time to 15 minutes from now
        user_timezone = pytz.utc
        # Convert current UTC time to user's local time zone
        local_time = timezone.now().astimezone(user_timezone)
        expiration_time = local_time + timezone.timedelta(minutes=15)

        # Save expiration time and temporary password to user object
        user.temporary_password = temporary_password
        user.temporary_password_created_at = expiration_time
        user.save()

        # send email to user
        try:
            send_forgot_password_email(user, name, reset_account_url, temporary_password)
            return Response({'message': 'Password reset link sent to your email'}, status=status.HTTP_200_OK)

        except BadHeaderError:
            return Response({'error': 'Could not send email'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["User"],
               description="API endpoint for confirming the password reset request and redirecting the user to the password reset form.")
class ForgotPasswordConfirm(GenericAPIView):
    """
    **Confirms the password reset request and redirects the user to the password reset form.**

    *Attributes:*

    - authentication_classes: A list of registration_authentication classes used for this view (empty in this case).
    - permission_classes: A list of permission classes used for this view (empty in this case).
    - serializer_class: The serializer class used to validate the request data (serializers.ForgotPasswordConfirmSerializer).

    *Methods:*

    *get(self, request, uidb64, token, args, kwargs):*

    - Takes a GET request with 'uidb64' and 'token' in the URL parameters.
    - Decodes the user ID from 'uidb64'.
    - Retrieves the user object associated with the user ID.
    - Verifies the password reset token.
    - Checks if the password reset link has expired.
    - Generates a temporary password reset link if valid.
    - Redirects the user to the password reset form if successful, otherwise returns an error response.

    *Raises:*

   - TypeError: If 'uidb64' is not a valid encoded string.
   -  ValueError: If 'uidb64' cannot be decoded.
   - OverflowError: If 'uidb64' is too long.
   - User.DoesNotExist: If no user is found with the provided user ID.

    **Returns:**

    Response:

    - 302 Found with a redirect to the password reset form if successful.
    - 400 Bad Request with an error message if the link is invalid or expired.

    **Notes:**

    - This view verifies the password reset token for security purposes.
    - The 'USER_PASSWORD_RESET_URL' environment variable must be set with the password reset URL template.
    """
    authentication_classes = []
    permission_classes = []
    serializer_class = serializers.ForgotPasswordConfirmSerializer

    @transaction.atomic
    def get(self, request, uidb64, token, *args, **kwargs):
        """

        """

        email = None

        user_password_reset_confirm_url = os.getenv('USER_PASSWORD_RESET_CONFIRM_URL')

        # generate temp token
        tk = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
            email = user.email

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # check if token has expired
        if user is not None and make_naive(user.temporary_password_created_at) < timezone.now():
            return Response({'error': 'Reset password link has expired'}, status=status.HTTP_400_BAD_REQUEST)

        if user is not None and TokenGenerator().check_token(user, token):

            reset_password_url = user_password_reset_confirm_url + tk + '&eml=' + email

            return redirect(reset_password_url)
        else:
            return Response({'error': 'Reset password link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)


# activate account
@extend_schema(tags=["User"], description="API endpoint for activating user accounts using email confirmation tokens.")
class ActivateAccount(GenericAPIView):
    """
    **Activates the user account using the provided activation token.**

        This method takes a GET request with the following URL parameters:

        - `uidb64`: The user ID encoded in base64.
        - `token`: The activation token.

    It performs the following actions:

        1. Decodes the user ID from `uidb64`.
        2. Retrieves the user object associated with the user ID.
        3. Verifies the activation token.
        4. Activates the user account if the token is valid.
        5. Redirects the user to the login page with a success message if successful.
        6. Returns an error message if the token is invalid or expired.

    **Raises:**

        - TypeError: If `uidb64` is not a valid encoded string.
        - ValueError: If `uidb64` cannot be decoded.
        - OverflowError: If `uidb64` is too long.
        - User.DoesNotExist: If no user is found with the provided user ID.

    **Returns:**

        - 302 Found with a redirect to the login page if successful.
        - 400 Bad Request with an error message if the token is invalid or expired.

    **Notes:**

        - This view verifies the activation token for security purposes.
        - The `USER_LOGIN_URL` environment variable must be set with the login URL template.

    """
    serializer_class = serializers.ActivationSerializer

    @staticmethod
    def get(request, uidb64, token, *args, **kwargs):
        """
        **Activates the user account using the provided activation token.**

        This method takes a GET request with the following URL parameters:

        - `uidb64`: The user ID encoded in base64.
        - `token`: The activation token.

        It performs the following actions:

        1. Decodes the user ID from `uidb64`.
        2. Retrieves the user object associated with the user ID.
        3. Verifies the activation token.
        4. Activates the user account if the token is valid.
        5. Redirects the user to the login page with a success message if successful.

        6. Returns an error message if the token is invalid or expired.

        **Raises:**

        - TypeError: If `uidb64` is not a valid encoded string.
        - ValueError: If `uidb64` cannot be decoded.
        - OverflowError: If `uidb64` is too long.

        """

        REDIRECT_TO_LOGIN_PAGE = os.getenv('REDIRECT_TO_LOGIN_PAGE')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and TokenGenerator().check_token(user, token):
            User.objects.filter(pk=user.pk).update(verified=True)
            User.objects.filter(pk=user.pk).update(is_active=True)

            return redirect(REDIRECT_TO_LOGIN_PAGE)
        else:
            return Response({'error': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)


# logout
@extend_schema(tags=["User"], description="API endpoint for logging out the authenticated user.")
class Logout(APIView):  # Logout the authenticated user
    """
    **Logs out the authenticated user by deleting their registration_authentication token.**

    This endpoint allows users to log out of the application by providing a valid logout token. This token is typically generated during user login and used to identify the user in subsequent requests.

    **Permissions:**

    * Requires user to be authenticated.

    **Responses:**

    * **200 OK:** User logged out successfully.

    * **400 Bad Request:**

        * User is not authenticated.
        * Invalid logout token provided.

    """
    serializer_class = serializers.EmptySerializer

    @staticmethod
    def post(request, *args, **kwargs):
        """
        **Logs out the user if they are authenticated.**

        This method checks if the user is authenticated and performs the following actions:

        * If the user is authenticated:
            * Deletes the user's registration_authentication token.
            * Returns a response with a success message and an HTTP 200 OK status code.

        * If the user is not authenticated:
            * Returns a response with an error message and an HTTP 400 Bad Request status code.

        Args:

            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments passed to the method.
            **kwargs: Additional keyword arguments passed to the method.

        Returns:

            HttpResponse: A response object containing the logout information and status code.

        Raises:

            None

        """
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)

        return Response({'error': 'User is not authenticated'}, status=status.HTTP_400_BAD_REQUEST)


# delete user account
@extend_schema(tags=["User"], description="API endpoint for deleting user accounts.")
class DeleteAccount(GenericAPIView):
    """
    **API view for handling account deletion requests.**

    Handle DELETE requests to permanently delete a user's account.

    Methods:
    -------
    delete(self, request, *args, **kwargs):

        Handle a DELETE request to delete the user's account.

    Raises:
    -------
    exceptions.PermissionDenied:

        If the user does not have permission to delete the account.
    exceptions.NotFound:

        If the specified account does not exist.

    Returns:
    --------
    Response:

        A response indicating the success or failure of the deletion,
        with an appropriate status code and message.

    """

    authentication_classes = [JWTAuthentication]  # user JWTAuthentication
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.DeleteAccountSerializer

    def get_object(self):
        """
        Retrieve and return the authenticated user
        """

        return self.request.user

    @transaction.atomic
    def put(self, request, pk):
        """
        Delete the authenticated user account
        :param request:
        :param pk:
        :return:
        """

        user = get_user_model().objects.get(pk=pk)  # get the user object

        # get the user profile
        serializer = self.serializers_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if user password is correct
        serializer.validated_data.get('password')
        if not user.check_password(serializer.validated_data.get('password')):
            return Response({'error': 'Password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        # do not allow more than 3 password attempts within one hour
        if user.password_attempts >= 3:
            last_attempt = user.password_attempt_time
            if last_attempt > timezone.now() - timezone.timedelta(hours=1):
                return Response({'error': 'Too many password attempts. Please try again later.'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                user.password_attempts = 0
                user.last_password_attempt = None

        # check if confirmation deletion is yes or no
        confirmation = self.request.data.get('confirmation')
        if confirmation == 'yes':
            try:
                user.delete()
                return Response({'message': 'User account deleted successfully'}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif confirmation == 'no':
            return Response({'message': 'User account deletion cancelled'}, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Invalid confirmation'}, status=status.HTTP_400_BAD_REQUEST)
