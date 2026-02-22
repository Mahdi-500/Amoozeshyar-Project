from django.contrib import admin
from .models import *

# Register your models here.
# @admin.register(student)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ['student_id', 'entrance_year', 'last_year', "modified"]
#     raw_id_fields = ["major", "university", "user"]

@admin.register(major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "capacity"]
    list_editable = ["capacity"]
    search_fields = ["name"]

@admin.register(university)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ["name", "code"]

@admin.register(group)
class GroupAdmin(admin.ModelAdmin):
    list_display= ["name", "code"]

@admin.register(professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "created", "modified"]
    raw_id_fields = ["universities"]

@admin.register(lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["name", "unit", "unit_type", "lesson_type"]
    #raw_id_fields = ["hamniaz", "lesson_major"]
    list_editable = ["unit", "unit_type", "lesson_type"]
    search_fields = ["name"]
    autocomplete_fields = ["lesson_major","pishniaz", "hamniaz"]

@admin.register(lesson_class)
class LessonClassAdmin(admin.ModelAdmin):
    list_display = ["lesson_code", "professor_name", "university_location", "group_name", "created", "modified"]

# @admin.register(Grade)
# class GradeAdmin(admin.ModelAdmin):
#     list_display = ["student_name", "lesson_name", "score", "created", "modified"]
#     list_editable = ["score"]

# @admin.register(student_choosing_lesson)
# class StudentChoosingAdmin(admin.ModelAdmin):
#     list_display = ["student_name", "chosen_class", "semester"]