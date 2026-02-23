from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "created", "modified"]
    raw_id_fields = ["universities"]

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["student_name", "lesson_name", "score", "created", "modified"]
    list_editable = ["score"]