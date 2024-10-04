from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, mixins, viewsets
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.models import Profile, ProfilePicture
from user.user_profile import serializers
from user.user_profile.serializers import UserProfileSerializer
from util.Image_processor.image_file_processor import convert_png_to_jpg
from util.Storage.process_image import default_profile_picture
from util.Storage.s3_function import delete_s3_file


@extend_schema(tags=['User Profile'])
class UserProfileViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    **API endpoint for managing user profiles.**

    Provides functionalities for:

        * Listing user profiles (GET /user-profiles/)
        * Retrieving a specific user profile (GET /user-profiles/<pk>/)
        * (Optional) Filtering profiles by first or last name (GET /user-profiles/?first_name=... or ?last_name=...)
        * (Optional) Ordering profiles by username (GET /user-profiles/?ordering=user__username)

    Permissions:

        * Accessing user profiles requires authentication (IsAuthenticatedOrReadOnly)
        * JWT token authentication is used (JWTAuthentication)

    Note:

        * Create and Delete functionalities are not implemented in this base viewset.
        * You'll need to implement them following the standard Django REST framework patterns.

    """
    serializer_class = serializers.UserProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication, ]  # JWT token authentication
    parser_classes = (MultiPartParser, JSONParser, FormParser)

    def get_queryset(self):
        """
         Retrieve and filter the user profile queryset based on query parameters.
        Allows ordering by any field using the `ordering` query parameter (defaults to `user__username`).
        Supports filtering by first name and last name using query parameters.
        """
        queryset = super().get_queryset()

        # Combine filters for efficient querying
        filters = {}
        first_name = self.request.query_params.get('first_name')
        if first_name:
            filters['user__first_name__icontains'] = first_name

        last_name = self.request.query_params.get('last_name')
        if last_name:
            filters['user__last_name__icontains'] = last_name

        queryset = queryset.filter(**filters)  # Apply combined filters in a single query

        # Handle ordering efficiently
        ordering = self.request.query_params.get('ordering', 'user__username')
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset


@extend_schema(tags=['User Profile'])
class UserProfileUpdate(APIView):
    """

    """
    serializer_class = serializers.UserProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication, ]  # JWT token authentication
    parser_classes = (MultiPartParser, JSONParser, FormParser)

    @extend_schema(operation_id='update_user_profile')
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        **Updates a user profile.**

        This method allows authenticated users to update their own profile information
        using a partial update. Only the provided fields in the request data will be updated.

        Args:

            request (Request): The incoming request object.
            user_id (int): The ID of the user profile to be updated.

        Returns:

            Response: A JSON response containing the update status or error message.

        """

        user = request.user
        print(user)

        try:
            user_profile = Profile.objects.get(id=pk)

        except Profile.DoesNotExist:
            return Response({"error": "User profile doesnt exist."}, status=status.HTTP_404_NOT_FOUND)

        # prevent unauthorized user from updating the profile of another user
        if user != user_profile.user:
            return Response({"error": "You are not authorized to update this profile."},
                            status=status.HTTP_403_FORBIDDEN)

        try:

            profile = Profile.objects.get(user=user_profile.user_id)
        except Profile.DoesNotExist:
            return Response({"error": "User profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(instance=profile, data=request.data, partial=True)

        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.username = request.data.get('username', user.username)

        user_profile.title_before = request.data.get('title_before', user_profile.title_before)
        user_profile.title_after = request.data.get('title_after', user_profile.title_after)
        user_profile.about = request.data.get('about', user_profile.about)
        user_profile.phone_number = request.data.get('phone_number', user_profile.phone_number)
        user_profile.date_of_birth = request.data.get('date_of_birth', user_profile.date_of_birth)
        user_profile.nationality = request.data.get('nationality', user_profile.nationality)
        user_profile.street_address = request.data.get('street_address', user_profile.street_address)
        user_profile.city = request.data.get('city', user_profile.city)
        user_profile.state = request.data.get('state', user_profile.state)
        user_profile.country = request.data.get('country', user_profile.country)
        user_profile.postal_code = request.data.get('postal_code', user_profile.postal_code)
        user_profile.website = request.data.get('website', user_profile.website)
        user_profile.linkedin = request.data.get('linkedin', user_profile.linkedin)

        try:

            if serializer.is_valid():
                user_profile.save()
                if user.first_name or user.last_name or user.username:
                    user.save()

                return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------GET USER PROFILE BY USERNAME--------------------------------
@extend_schema(tags=['User Profile'])
class UserProfileByUserName(APIView):
    """
    **This API endpoint retrieves a user profile based on the provided username.**

    *Permissions:*

        * IsAuthenticatedOrReadOnly: Allows access to both authenticated and anonymous users.
            * Authenticated users can access any profile.
            * Anonymous users can only access their own profile (if logged in).
    *Authentication:*

        * JWTAuthentication: Uses JSON Web Tokens for authentication.

    *Parameters:*

        * username (str): The username of the user whose profile is being retrieved.

    *Returns:*

        * A JSON response containing the serialized user profile data on success (status code 200).
        * A JSON response with an error message "User profile does not exist." on failure (status code 404).

    *Raises:*
        * Profile.DoesNotExist: If no profile is found for the provided username.

    """
    serializer_class = serializers.UserProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = [JWTAuthentication, ]
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    @extend_schema(operation_id='get_user_profile_by_username')
    def get(self, request, username, *args, **kwargs):
        """
        Retrieves a user profile based on the username.
        """
        try:
            user_profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return Response({"error": "User profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------USER PROFILE PICTURE--------------------------------
@extend_schema(tags=['User Profile'])
class ProfilePictureView(APIView):
    """

    """

    queryset = ProfilePicture.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = [JWTAuthentication, ]
    parser_classes = (MultiPartParser, JSONParser, FormParser)
    serializer_class = serializers.ProfilePictureSerializer

    @extend_schema(operation_id='get_profile_picture')
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve the profile picture of a user profile by user id.
        """
        try:
            user_profile_picture = self.queryset.get(user_profile=pk)
            serializer = self.serializer_class(user_profile_picture)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({"error": "User profile does not exist."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(operation_id='update_profile_picture')
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Update the profile picture of a user profile by user id.
        """

        user = request.user
        user_profile = get_object_or_404(Profile, user=user, pk=pk)

        # prevent unauthorized user from updating the profile picture of another user
        if user != user_profile.user:
            return Response(
                {"error": "You are not authorized to update this profile picture."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile_image = user_profile.profile_images.profile_picture

        if profile_image:
            # delete profile picture from s3 bucket
            delete_s3_file(str(user_profile.profile_images.profile_picture))
            profile_image.delete()

        get_profile_image = request.data.get('profile_picture')

        # Add default profile picture if no profile picture is uploaded
        if not get_profile_image:
            default_profile_picture(user, user_profile, pk)
            return Response({'message': 'Profile picture updated successfully'}, status=status.HTTP_200_OK)

        check_png = convert_png_to_jpg(get_profile_image)  # convert image to png
        process_profile_image = check_png

        ProfilePicture.objects.filter(user_profile=pk).update_or_create(
            user_profile=user_profile,
            defaults={'profile_picture': process_profile_image}
        )

        return Response({'message': 'Profile picture updated successfully'}, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk):
        """
        Delete the profile picture of a user profile by user id.
        """
        user = request.user
        user_profile = get_object_or_404(Profile, pk=pk)

        # prevent unauthorized user from updating the profile picture of another user
        if user_profile.user != user:
            return Response(
                {"error": "You are not authorized to delete this profile picture."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile_pictures = ProfilePicture.objects.filter(user_profile=pk)

        try:
            # delete profile picture from s3 bucket
            delete_s3_file(str(user_profile.profile_images.profile_picture))

            # delete profile picture from database
            profile_pictures.delete()

            # set default profile picture
            default_profile_picture(user, user_profile, pk)

            return Response({'message': 'Profile picture deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
