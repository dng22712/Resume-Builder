from cvbuilder.models import Education
from rest_framework import serializers


class CvEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            'id',
            'user',
            'cv',
            'school_name',
            'school_city',
            'school_country',
            'degree',
            'field_of_study',
            'grade',
            'start_date',
            'end_date',
            'currently_studying_here',
            'created_at',
            'updated_at'

        )

        extra_kwargs = {'id': {'read_only': True}}

