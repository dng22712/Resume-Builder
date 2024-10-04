from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from user.models import Profile, ProfilePicture


class ProfilePictureSerializer(serializers.ModelSerializer):
    """Serializer for the profile picture model"""

    class Meta:
        model = ProfilePicture
        fields = '__all__'

        extra_kwargs = {'id': {'read_only': True}}


# user profile serializers
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the user profile model"""
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    profile_picture = serializers.SerializerMethodField()

    @extend_schema_field(serializers.DictField)
    def get_profile_picture(self, user_profile):
        profile_pictures = ProfilePicture.objects.filter(user=user_profile.user).first()
        if profile_pictures:
            return ProfilePictureSerializer(profile_pictures).data  # No need for many=True
        else:
            return None  # Or an empty dictionary if no picture exists

    class Meta:
        model = Profile
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'title_before',
            'title_after',
            'about',
            'phone_number',
            'date_of_birth',
            'nationality',
            'street_address',
            'city',
            'state',
            'country',
            'postal_code',
            'website',
            'profile_picture',

        )
        extra_kwargs = {'id': {'read_only': True}}
