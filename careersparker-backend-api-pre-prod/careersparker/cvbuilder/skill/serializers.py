
from rest_framework import serializers

from cvbuilder.models import Skill


class CvSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}

