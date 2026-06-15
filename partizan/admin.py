from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'active', 'duration', 'min_age', 'max_age', 'max_children')
    list_filter = ('category', 'active')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')
    list_editable = ('active',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'title', 'slug', 'image', 'description', 'active')
        }),
        ('Характеристики', {
            'fields': ('duration', 'price', 'min_age', 'max_age', 'max_children')
        }),
    )

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'city', 'date', 'order')
    list_filter = ('place', 'date', 'city')
    list_editable = ('order',)
    search_fields = ('title',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'date', 'image', 'order')
        }),
        ('Детали соревнования', {
            'fields': ('place', 'city', 'competition_name', 'age_category')
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at', 'approved')
    list_filter = ('approved', 'rating')
    actions = ['approve_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
    approve_reviews.short_description = "Одобрить выбранные отзывы"

@admin.register(QuickOrder)
class QuickOrderAdmin(admin.ModelAdmin):
    list_display = ('holiday', 'phone', 'created_at', 'processed')
    list_filter = ('processed', 'created_at')
    search_fields = ('phone', 'holiday__title')
    actions = ['mark_processed']
    
    def mark_processed(self, request, queryset):
        queryset.update(processed=True)
    mark_processed.short_description = "Пометить обработанными"

@admin.register(FullOrder)
class FullOrderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'holiday', 'selected_date', 'selected_time', 'children_count', 'age_of_children', 'created_at', 'processed')
    list_filter = ('processed', 'created_at', 'holiday', 'selected_date')
    search_fields = ('full_name', 'phone', 'holiday__title')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Контактная информация', {
            'fields': ('full_name', 'phone')
        }),
        ('Детали заявки', {
            'fields': ('holiday', 'selected_date', 'selected_time', 'children_count', 'age_of_children', 'notes')
        }),
        ('Дата создания и статус', {
            'fields': ('created_at', 'processed')
        }),
    )
    actions = ['mark_processed']
    
    def mark_processed(self, request, queryset):
        queryset.update(processed=True)
    mark_processed.short_description = "Пометить обработанными"

@admin.register(TrainingRegistration)
class TrainingRegistrationAdmin(admin.ModelAdmin):
    list_display = ('parent_name', 'child_name', 'phone', 'age_group', 'visit_type', 'created_at', 'processed')
    list_filter = ('age_group', 'visit_type', 'processed', 'created_at')
    search_fields = ('parent_name', 'child_name', 'phone')
    actions = ['mark_processed']
    
    def mark_processed(self, request, queryset):
        queryset.update(processed=True)
    mark_processed.short_description = "Пометить обработанными"