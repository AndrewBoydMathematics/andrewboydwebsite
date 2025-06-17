from django.contrib import admin
from .models import Artwork, CommissionRequest, PayPalAccount, ModelApplication, ModelImage, SiteSettings

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'medium', 'category', 'price', 'created_at')
    list_filter = ('status', 'medium', 'category')
    search_fields = ('title', 'description')

@admin.register(CommissionRequest)
class CommissionRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status', 'medium', 'category', 'budget', 'created_at')
    list_filter = ('status', 'medium', 'category')
    search_fields = ('name', 'email', 'description')

@admin.register(PayPalAccount)
class PayPalAccountAdmin(admin.ModelAdmin):
    list_display = ('title', 'email', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Account Information', {
            'fields': ('title', 'email', 'client_id')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class ModelImageInline(admin.TabularInline):
    model = ModelImage
    extra = 0

@admin.register(ModelApplication)
class ModelApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'modeling_type', 'status', 'created_at')
    list_filter = ('status', 'modeling_type')
    search_fields = ('name', 'email', 'description')
    inlines = [ModelImageInline]
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Application Details', {
            'fields': ('modeling_type', 'description', 'availability', 'additional_info')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance of SiteSettings
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only instance
        return False 