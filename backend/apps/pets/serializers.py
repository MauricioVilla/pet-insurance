from rest_framework import serializers
from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Pet
        fields = ('id', 'owner', 'name', 'species', 'birth_date',
                  'coverage_start', 'coverage_end', 'created_at')
        read_only_fields = ('id', 'coverage_end', 'created_at')


class PetReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ('id', 'name', 'species', 'birth_date',
                  'coverage_start', 'coverage_end', 'created_at')
        read_only_fields = fields
