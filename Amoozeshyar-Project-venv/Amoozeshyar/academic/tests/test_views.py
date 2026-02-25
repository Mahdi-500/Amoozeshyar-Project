from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User, Group

class testGeneralViews(TestCase):
    def setUp(self):
        admin = User.objects.create_user(username="testadmin", password="test")
        test_professor = User.objects.create_user(username="testprofessor", password="test")
        student = User.objects.create_user(username="teststudent", password="test")

        Group.objects.create(name="admin")
        Group.objects.create(name="professor")
        Group.objects.create(name="student")

        admin.groups.add(Group.objects.get(name="admin"))
        student.groups.add(Group.objects.get(name="student"))
        test_professor.groups.add(Group.objects.get(name="professor"))



    def test_login_view(self):
        response = self.client.get(reverse("academic:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Login.html")



    def test_main_view(self):
        response = self.client.get(reverse("academic:main"))
        self.assertRedirects(response, "/?next=/main/")
        self.assertTemplateNotUsed(response, "main.html")
        
        # ? testing with admin privilages
        self.client.login(username="testadmin", password="test")
        response_after_admin_login = self.client.get(reverse("academic:main"))
        self.assertTemplateUsed(response_after_admin_login, "main.html")
        self.assertContains(response_after_admin_login, "ثبت نام دانشجو")
        self.assertContains(response_after_admin_login, "ثبت نام استاد")
        self.assertContains(response_after_admin_login, "ثبت نام استاد")
        self.assertContains(response_after_admin_login, "ایجاد کلاس")
        self.assertContains(response_after_admin_login, "ایجاد درس")
        self.assertContains(response_after_admin_login,  "جتسجوی کلاس درس")

        # ? testing with professor privilages
        self.client.login(username="testprofessor", password="test")
        response_after_professor_login = self.client.get(reverse("academic:main"))
        self.assertTemplateUsed(response_after_professor_login, "main.html")
        self.assertContains(response_after_professor_login, "پروفایل")


        # ? testing with student privilages
        self.client.login(username="teststudent", password="test")
        response_after_student_login = self.client.get(reverse("academic:main"))
        self.assertTemplateUsed(response_after_student_login, "main.html")
        self.assertContains(response_after_student_login, "انتخاب واحد")
        self.assertContains(response_after_student_login, "جتسجوی کلاس درس")



    def test_lesson_form_view(self):
        response = self.client.get(reverse("academic:create_lesson"))
        self.assertRedirects(response, "/?next=/create_lesson")
        self.assertTemplateNotUsed(response, "regiister_professor.html")

        # ? after login
        self.client.login(username="testadmin", password="test")
        response_after_login = self.client.get(reverse("academic:create_lesson"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "register_professor.html")

        

    def test_lesson_class_form_view(self):
        response = self.client.get(reverse("academic:lesson_class"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/create_class")
        self.assertTemplateNotUsed(response, "add_lesson_class.html")

        # ? after login
        self.client.login(username="testadmin", password="test")
        response_after_login = self.client.get(reverse("academic:lesson_class"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "add_lesson_class.html")