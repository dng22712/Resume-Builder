from cvbuilder.models import Education, Certificate
from rest_framework import serializers


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

