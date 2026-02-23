from django.urls import path
from . import views

app_name = "academic"
urlpatterns = [
    path("", views.login_form_view, name="login"),
    path("main/", views.MainView, name="main"),
]