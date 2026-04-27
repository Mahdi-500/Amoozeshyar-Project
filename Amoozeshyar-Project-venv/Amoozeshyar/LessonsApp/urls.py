from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "lesson"
urlpatterns = [
    path("create_lesson", views.lesson_form_view, name="create_lesson"),
    path("create_class", views.lesson_class_form_view, name="lesson_class"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)