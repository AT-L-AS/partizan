from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'active')
    list_filter = ('category', 'active')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')

@admin.register(HolidayDate)
class HolidayDateAdmin(admin.ModelAdmin):
    list_display = ('holiday', 'date', 'available', 'current_bookings', 'max_bookings')
    list_filter = ('date', 'available')
    search_fields = ('holiday__title',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'city', 'date', 'order')
    list_filter = ('place', 'date', 'city')
    list_editable = ('order',)
    search_fields = ('title', )
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'date', 'image', 'order')
        }),
        ('Детали соревнования', {
            'fields': ('place', 'city', 'age_category')
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'created_at', 'approved')
    list_filter = ('approved', 'rating')
    actions = ['approve_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
    approve_reviews.short_description = "Одобрить"

@admin.register(QuickOrder)
class QuickOrderAdmin(admin.ModelAdmin):
    list_display = ('holiday', 'phone', 'created_at', 'processed')
    list_filter = ('processed', 'created_at')
    actions = ['mark_processed']
    
    def mark_processed(self, request, queryset):
        queryset.update(processed=True)
    mark_processed.short_description = "Пометить обработанными"

@admin.register(FullOrder)
class FullOrderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'holiday', 'holiday_date', 'phone', 'created_at', 'processed')
    list_filter = ('processed', 'created_at')
    search_fields = ('full_name', 'phone')
    actions = ['mark_processed']
    
    def mark_processed(self, request, queryset):
        queryset.update(processed=True)
    mark_processed.short_description = "Пометить обработанными"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('phone', 'email', 'address')

@admin.register(TrainingRegistration)
class TrainingRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_name', 'child_name', 'phone', 'get_age_group_display', 'get_visit_type_display', 'created_at', 'processed')
    list_filter = ('age_group', 'visit_type', 'processed', 'created_at')
    search_fields = ('parent_name', 'child_name', 'phone')
    list_display_links = ('id', 'parent_name')
    list_editable = ('processed',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Информация о заявителе', {
            'fields': ('parent_name', 'phone')
        }),
        ('Информация о ребенке', {
            'fields': ('child_name', 'child_age', 'age_group')
        }),
        ('Детали заявки', {
            'fields': ('visit_type', 'created_at', 'processed')
        }),
    )
    
    actions = ['mark_as_processed', 'mark_as_not_processed']
    
    def mark_as_processed(self, request, queryset):
        updated = queryset.update(processed=True)
        self.message_user(request, f'{updated} заявок помечено как обработанные')
    mark_as_processed.short_description = "Пометить как обработанные"
    
    def mark_as_not_processed(self, request, queryset):
        updated = queryset.update(processed=False)
        self.message_user(request, f'{updated} заявок помечено как необработанные')
    mark_as_not_processed.short_description = "Пометить как необработанные"
    
    def get_age_group_display(self, obj):
        return dict(TrainingRegistration.GROUP_CHOICES).get(obj.age_group, obj.age_group)
    get_age_group_display.short_description = "Группа"
    
    def get_visit_type_display(self, obj):
        return dict(TrainingRegistration.VISIT_CHOICES).get(obj.visit_type, obj.visit_type)
    get_visit_type_display.short_description = "Тип посещения"