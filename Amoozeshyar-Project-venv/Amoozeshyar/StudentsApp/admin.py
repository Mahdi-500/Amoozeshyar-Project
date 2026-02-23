from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'entrance_year', 'last_year', "modified"]
    raw_id_fields = ["major", "university", "user"]

@admin.register(student_choosing_lesson)
class StudentChoosingAdmin(admin.ModelAdmin):
    list_display = ["student_name", "chosen_class", "semester"]