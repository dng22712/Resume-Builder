
from rest_framework import serializers

from cvbuilder.models import Skill, Strength


class StrengthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strength
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}

