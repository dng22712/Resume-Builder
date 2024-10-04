
from rest_framework import serializers

from cvbuilder.models import Skill, Strength, Graph


class GraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graph
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}

