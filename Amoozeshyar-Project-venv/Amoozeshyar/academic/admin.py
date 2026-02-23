from django.contrib import admin
from .models import *

# Register your models here.
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