from django.contrib import admin
from .models import Claim


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet', 'owner', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('owner__email', 'pet__name')
    readonly_fields = ('invoice_hash', 'created_at', 'updated_at')
