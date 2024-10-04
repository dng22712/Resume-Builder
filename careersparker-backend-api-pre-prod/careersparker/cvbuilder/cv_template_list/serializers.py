from rest_framework import serializers

from cvbuilder.models import CvTemplateList


class CvTemplateListSerializer(serializers.ModelSerializer):
	class Meta:
		model = CvTemplateList
		fields = ('id', 'cv_template_name', 'cv_template_thumbnail')

		extra_kwargs = {'id': {'read_only': True}}
