from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path("register-student", views.student_form_view, name="register_student"),
    path("search", views.student_lesson_search_view, name="lesson_search"),
    path("choosing_lesson", views.choosing_lesson_form_view, name="choosing_lesson"),
    path("pre-saving", views.temporarely_saving_chosen_lesson_view, name="pre_save"),
    path("submiting", views.submiting_the_chosen_lesson,name="submit"),
    path("student_report", views.student_report_view, name="student_report"),
]
