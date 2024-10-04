from cvbuilder.models import Education
from rest_framework import serializers


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

