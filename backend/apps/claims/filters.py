import django_filters
from .models import Claim, ClaimStatus


class ClaimFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=ClaimStatus.choices)
    pet = django_filters.NumberFilter(field_name='pet__id')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Claim
        fields = ('status', 'pet', 'created_after', 'created_before')
