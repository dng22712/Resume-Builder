from cvbuilder.models import EmploymentHistory
from rest_framework import serializers


class EmploymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentHistory
        fields = (
            'id',
            'user',
            'cv',
            'job_title',
            'employer_name',
            'employer_city',
            'employer_country',
            'start_date',
            'end_date',
            'currently_working_here',
            'job_description',
            'created_at',
            'updated_at'
        )
