from cvbuilder.models import Publication, Achievement
from rest_framework import serializers


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

