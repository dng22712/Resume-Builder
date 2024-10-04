from cvbuilder.models import Reference
from rest_framework import serializers


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

