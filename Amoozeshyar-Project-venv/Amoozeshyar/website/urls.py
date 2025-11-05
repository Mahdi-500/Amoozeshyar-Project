from django.urls import path
from . import views

app_name = "website"
urlpatterns = [
    path("", views.login_form_view, name="login"),
    path("main/", views.MainView, name="main"),
    path("register-student", views.student_form_view, name="register_student"),
    path("register-professor", views.professor_form_view, name="register_professor"),
    path("create_lesson", views.lesson_form_view, name="create_lesson"),
    path("create_class", views.lesson_class_form_view, name="lesson_class"),
    path("professor/profile", views.professor_profile_view, name="professor_profile"),
    path("professor/classes/<str:p_code>/<str:u_code>", views.professor_lesson_list_view, name="professor_lessons"),
    path('professor/lesson/details/<str:l_code>', views.professor_lesson_details, name="lesson_detail"),
    path("search", views.lesson_search_view, name="lesson_search"),
    path("choosing_lesson", views.choosing_lesson_form_view, name="choosing_lesson"),
    path("saving", views.saving_chosen_lesson_view, name="save"),
    path("professor/lesson/details/<str:l_code>/<int:class_code>/submitting_grade", views.grade_form_view, name="grade")
]