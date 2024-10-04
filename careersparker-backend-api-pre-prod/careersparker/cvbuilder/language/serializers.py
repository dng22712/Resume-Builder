

from cvbuilder.models import Reference, Internship, Course, Language
from rest_framework import serializers


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

