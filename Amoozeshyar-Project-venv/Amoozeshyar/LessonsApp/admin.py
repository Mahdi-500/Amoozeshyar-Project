from django.contrib import admin
from .models import *
# Register your models here.
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