
from rest_framework import serializers

from cvbuilder.models import Skill, Strength, CustomSection


class CustomSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomSection
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}

