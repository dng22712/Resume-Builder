from cvbuilder.models import Publication, Achievement, Hobby
from rest_framework import serializers


class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

