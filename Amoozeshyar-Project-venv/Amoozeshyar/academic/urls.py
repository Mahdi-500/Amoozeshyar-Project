from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "academic"
urlpatterns = [
    path("", views.login_form_view, name="login"),
    path("main/", views.MainView, name="main"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)