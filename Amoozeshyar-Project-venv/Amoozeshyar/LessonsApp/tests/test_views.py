from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User, Group

class TestLessonViews(TestCase):
    def setUp(self):
        admin = User.objects.create_user(username="testadmin", password="test")
        Group.objects.create(name="admin")
        admin.groups.add(Group.objects.get(name="admin"))



    def test_lesson_form_view(self):
        response = self.client.get(reverse("lesson:create_lesson"))
        self.assertRedirects(response, "/?next=/create_lesson")
        self.assertTemplateNotUsed(response, "regiister_professor.html")

        # ? after login
        self.client.login(username="testadmin", password="test")
        response_after_login = self.client.get(reverse("lesson:create_lesson"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "register_lesson.html")

        

    def test_lesson_class_form_view(self):
        response = self.client.get(reverse("lesson:lesson_class"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/create_class")
        self.assertTemplateNotUsed(response, "add_lesson_class.html")

        # ? after login
        self.client.login(username="testadmin", password="test")
        response_after_login = self.client.get(reverse("lesson:lesson_class"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "add_lesson_class.html")