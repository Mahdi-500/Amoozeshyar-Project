from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path("register-student", views.student_form_view, name="register_student"),
    path("search", views.student_lesson_search_view, name="lesson_search"),
    path("choosing_lesson", views.choosing_lesson_form_view, name="choosing_lesson"),
    path("saving", views.saving_chosen_lesson_view, name="save"),

]
