

from cvbuilder.models import Reference, Internship, Course, Language, Volunteering
from rest_framework import serializers


class VolunteeringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volunteering
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

