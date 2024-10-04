from cvbuilder.models import Reference, Internship, Course
from rest_framework import serializers


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

