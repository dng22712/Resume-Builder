from cvbuilder.models import CvBuilder
from rest_framework import serializers


class CvBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CvBuilder
        fields = '__all__'

        extra_kwargs = {'id': {'read_only': True}}

    # validate the cvBuilder serializer
    def validate(self, data):
        """Validate the cv builder serializer"""

        # TODO: Add validation for cv_template_selected
        # pass
        required_fields = ['cv_title']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            raise serializers.ValidationError(
                {'error': f'Please enter the following fields: {", ".join(missing_fields)}'})

        return data



