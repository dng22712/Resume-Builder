
from rest_framework import serializers

from cvbuilder.models import Skill, Strength, Graph, TextSection


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextSection
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}

