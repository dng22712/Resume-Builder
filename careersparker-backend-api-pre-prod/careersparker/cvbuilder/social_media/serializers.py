

from cvbuilder.models import Reference, Internship, Course, Language, Volunteering, social_media
from rest_framework import serializers


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = social_media
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}


