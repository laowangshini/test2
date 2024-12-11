from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, Survey, MediaItem

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'display_name', 'user_type', 'is_staff', 'created_at')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'display_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('display_name', 'user_type')}),
        (_('权限信息'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('重要日期'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'display_name', 'password1', 'password2', 'user_type'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

class MediaItemInline(admin.TabularInline):
    model = MediaItem
    extra = 1

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('name', 'investigator', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name', 'investigator__username')
    inlines = [MediaItemInline]

@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'survey', 'media_type', 'category', 'created_at')
    list_filter = ('media_type', 'category')
    search_fields = ('title', 'description', 'survey__name')

admin.site.register(UserProfile, CustomUserAdmin)
