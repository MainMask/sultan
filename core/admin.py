from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Trainer, Athlete, Group, Exercise, Training, Report


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'role', 'linked_to', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('SULTAN', {'fields': ('role', 'linked_to')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SULTAN', {'fields': ('role', 'linked_to')}),
    )


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'experience', 'phone')
    search_fields = ('full_name',)


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'group', 'trainer', 'enrolled_at')
    list_filter = ('group', 'trainer')
    search_fields = ('full_name',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'level', 'max_count')
    list_filter = ('level',)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'load_type', 'unit')
    list_filter = ('load_type',)
    search_fields = ('name',)


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('date', 'athlete', 'exercise', 'sets', 'reps', 'weight', 'is_locked')
    list_filter = ('is_locked', 'exercise__load_type', 'date')
    search_fields = ('athlete__full_name', 'exercise__name')
    date_hierarchy = 'date'
    actions = ['lock_selected', 'unlock_selected']

    @admin.action(description='Заблокировать выбранные')
    def lock_selected(self, request, queryset):
        queryset.update(is_locked=True)

    @admin.action(description='Разблокировать выбранные')
    def unlock_selected(self, request, queryset):
        queryset.update(is_locked=False)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('type', 'athlete', 'group', 'period_start', 'period_end', 'created_at')
    list_filter = ('type',)
