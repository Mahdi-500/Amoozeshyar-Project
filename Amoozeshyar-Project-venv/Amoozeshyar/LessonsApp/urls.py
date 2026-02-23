from django.urls import path
from . import views

app_name = "lesson"
urlpatterns = [
    path("create_lesson", views.lesson_form_view, name="create_lesson"),
    path("create_class", views.lesson_class_form_view, name="lesson_class"),
]
