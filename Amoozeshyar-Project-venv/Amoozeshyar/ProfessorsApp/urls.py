from django.urls import path
from . import views

app_name = "professor"

urlpatterns = [
    path("register-professor", views.professor_form_view, name="register_professor"),
    path("professor/profile", views.professor_profile_view, name="professor_profile"),
    path("professor/classes/<str:p_code>/<str:u_code>", views.professor_lesson_list_view, name="professor_lessons"),
    path('professor/lesson/details/<str:l_code>', views.professor_lesson_details, name="lesson_detail"),
    path("professor/lesson/details/<str:l_code>/<int:class_code>/submitting_grade", views.grade_form_view, name="grade")
]
