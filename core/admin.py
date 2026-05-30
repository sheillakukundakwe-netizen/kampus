from django.contrib import admin

from .models import ClaimRequest, Item, Profile


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'location', 'reporter', 'claimed_by', 'is_resolved', 'reported_at')
    list_filter = ('status', 'location', 'is_resolved')
    search_fields = ('title', 'description', 'location', 'contact_info')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'campus_role', 'verified')
    search_fields = ('user__email',)


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'requester', 'status', 'created_at', 'responded_at')
    list_filter = ('status',)
    search_fields = ('item__title', 'requester__email', 'message')
