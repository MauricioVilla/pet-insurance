from rest_framework import serializers
from ..models import Pet


class PetSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Pet
        fields = ('id', 'owner', 'name', 'species', 'birth_date',
                  'status', 'status_display', 'coverage_start', 'coverage_end', 'created_at')
        read_only_fields = ('id', 'status', 'status_display', 'coverage_start', 'coverage_end', 'created_at')


class PetReadSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True, default='')
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Pet
        fields = ('id', 'name', 'species', 'birth_date',
                  'status', 'status_display', 'owner_name', 'owner_email',
                  'coverage_start', 'coverage_end', 'created_at')
        read_only_fields = fields
