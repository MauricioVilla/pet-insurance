from django.contrib import admin
from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'owner', 'coverage_start', 'coverage_end')
    list_filter = ('species',)
    search_fields = ('name', 'owner__email')
