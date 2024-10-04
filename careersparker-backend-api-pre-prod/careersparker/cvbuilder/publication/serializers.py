from cvbuilder.models import Publication
from rest_framework import serializers


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = "__all__"

        extra_kwargs = {'id': {'read_only': True}}

