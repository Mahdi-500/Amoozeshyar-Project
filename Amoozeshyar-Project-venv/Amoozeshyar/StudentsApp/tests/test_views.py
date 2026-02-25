from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User, Group

class testStudentViews(TestCase):

    def setUp(self):
        student = User.objects.create_user(username="teststudent", password="test")
        Group.objects.create(name="student")
        student.groups.add(Group.objects.get(name="student"))



    def test_student_form_view(self):
        response = self.client.get(reverse("academic:register_student"))
        self.assertRedirects(response, "/?next=/register-student")
        self.assertTemplateNotUsed(response, "register_student.html")

        # ? after login
        self.client.login(username="teststudent", password="test")
        response_after_login = self.client.get(reverse("academic:register_student"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "register_student.html")



    def test_lesson_search_view(self):
        response = self.client.get(reverse("academic:lesson_search"))
        self.assertRedirects(response, "/?next=/search")
        self.assertTemplateNotUsed(response, "lesson_search_result.html")

        # ? after login
        self.client.login(username="teststudent", password="test")
        response_after_login = self.client.get(reverse("academic:lesson_search"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "lesson_search_result.html")



    def test_choosing_lesson_form_view(self):
        response = self.client.get(reverse("academic:choosing_lesson"))
        self.assertRedirects(response, "/?next=/choosing_lesson")
        self.assertTemplateNotUsed(response, "lesson_search_result.html")

        # ? after login
        self.client.login(username="teststudent", password="test")
        response_after_login = self.client.get(reverse("academic:choosing_lesson"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed("lesson_search_result.htnl")
    


    def test_saving_chosen_lesson_view(self):
        response = self.client.get(reverse("academic:save"))
        self.assertRedirects(response, "/?next=/saving")
        self.assertTemplateNotUsed("choosing_lesson.html")

        # ? after login
        self.client.login(username="teststudent", password="test")
        response_after_login = self.client.get(reverse("academic:save"))
        self.assertRedirects(response_after_login, "/choosing_lesson")