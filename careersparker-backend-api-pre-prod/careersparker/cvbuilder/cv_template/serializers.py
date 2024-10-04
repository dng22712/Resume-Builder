from cvbuilder.models import Publication, Achievement, Hobby, CvTemplate
from rest_framework import serializers


class CvTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CvTemplate
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

