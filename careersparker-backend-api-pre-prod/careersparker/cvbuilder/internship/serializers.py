from cvbuilder.models import Reference, Internship
from rest_framework import serializers


class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

