from django.urls import reverse
from django.test import TestCase
from django_jalali.db.models import jdatetime
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from ..forms import *
from ..models import university, major
from StudentsApp.models import student

class testLoginAndLogoutView(TestCase):
    def setUp(self):
        self.test_admin = User.objects.create_user(username="test_admin", password="test_pass")
        self.admin_gp = Group.objects.create(name="admin")



    def test_wrong_credentials(self):
        form_data = {
            "username":"test",
            "password":"test"
        }
        response = self.client.post(reverse("academic:login"), data={**form_data}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "نام کاربری یا رمز عبور صحیح نیست")
        self.assertRedirects(response, reverse("academic:login"))
    


    def test_no_group_assigned(self):
        form_data = {
            "username":"test_admin",
            "password":"test_pass"
        }
        response = self.client.post(reverse("academic:login"), data={**form_data}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "گروهی برای شما تعیین نشده است")
        self.assertRedirects(response, reverse("academic:login"))
    


    def test_login_page_accessible(self):
        response = self.client.get(reverse("academic:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Login.html")
        self.assertIsInstance(response.context["form"], LoginForm)



    def test_with_correct_credentials(self):
        self.test_admin.groups.add(self.admin_gp)
        form_data = {
            "username":"test_admin",
            "password":"test_pass"
        }
        response = self.client.post(reverse("academic:login"), data={**form_data}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "وارد شدید")
        self.assertRedirects(response, reverse("academic:main"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)



    def test_logout(self):
        self.client.login(username="test_admin", password="test_pass")
        self.client.logout()
        self.assertEqual(len(self.client.session.keys()), 0)
        response = self.client.get(reverse("academic:main"))
        self.assertRedirects(response, "/?next=/main/")



class testMainView(TestCase):
    def test_content_of_main_view_as_student(self):
        # ? creating student
        test_student = User.objects.create_user(username="test_student", password="test_pass")
        test_uni = university.objects.create(name="test", code=500, address="test")
        test_major = major.objects.create(name="test", code=100, capacity=1000)

        Group.objects.create(name="student")
        test_student.groups.add(Group.objects.get(name="student"))

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        data = {
            "user_id":test_student.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "major":test_major,
            "university":test_uni,
            "photo":photo
        }

        student.objects.create(**data)
        
        # ? tests
        self.client.login(username="test_student", password="test_pass")
        response = self.client.get(reverse("academic:main"))
        session = self.client.session
        
        # ? check template content
        self.assertContains(response, "انتخاب واحد")
        self.assertContains(response, "جستجوی کلاس درس")
        self.assertContains(response, "کارنامه")
        self.assertContains(response, "دانشجو")

        # ? Check session was initialized
        self.assertEqual(session["chosen_classes"], [])


    def test_content_of_main_view_as_professor(self):
        test_professor = User.objects.create_user(username="test_professor", password="test_pass")
        Group.objects.create(name="professor")
        test_professor.groups.add(Group.objects.get(name="professor"))

        self.client.login(username="test_professor", password="test_pass")
        response = self.client.get(reverse("academic:main"))
        self.assertContains(response, "پروفایل")
        
    

    def test_content_of_main_view_as_admin(self):
        admin = User.objects.create_user(username="test_admin", password="test_pass")
        Group.objects.create(name="admin")
        admin.groups.add(Group.objects.get(name="admin"))

        self.client.login(username="test_admin", password="test_pass")
        response = self.client.get(reverse("academic:main"))
        self.assertContains(response, "ثبت نام دانشجو")
        self.assertContains(response, "ثبت نام استاد")
        self.assertContains(response, "ایجاد کلاس")
        self.assertContains(response, "ایجاد درس")
        self.assertContains(response, "جستجوی کلاس درس")




    def test_context_values_for_others(self):
        admin = User.objects.create_user(username="test_admin", password="test_pass")
        Group.objects.create(name="admin")
        admin.groups.add(Group.objects.get(name="admin"))

        self.client.login(username="test_admin", password="test_pass")
        response = self.client.get(reverse("academic:main"))
        expected_keys = ["group", "user", "student", "student_status_flag"]
        for i in expected_keys:
            self.assertIn(i, response.context.keys())

        # ? checking expected value
        self.assertIsInstance(response.context["group"], Group)
        self.assertIsInstance(response.context["user"], User)
        self.assertEqual(response.context["student"], "")
        self.assertIs(type(response.context["student_status_flag"]), bool)



    def test_context_values_for_student(self):
        # ? creating student
        test_student = User.objects.create_user(username="test_student", password="test_pass")
        test_uni = university.objects.create(name="test", code=500, address="test")
        test_major = major.objects.create(name="test", code=100, capacity=1000)

        Group.objects.create(name="student")
        test_student.groups.add(Group.objects.get(name="student"))

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        data = {
            "user_id":test_student.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "major":test_major,
            "university":test_uni,
            "photo":photo
        }
        test_student_obj = student.objects.create(**data)

        self.client.login(username="test_student", password="test_pass")
        response = self.client.get(reverse("academic:main"))
        self.assertIsInstance(response.context["student"], student)
        self.assertIsNotNone(response.context["student"])
        self.assertEqual(response.context["group"].name, "student")
        self.assertIs(response.context["student_status_flag"], True)    # ? student status is مشغول

        # ? student status is not مشغول
        test_student_obj.status = "فارغ"
        test_student_obj.save()
        response_after_status_change = self.client.get(reverse("academic:main"))
        self.assertIs(response_after_status_change.context["student_status_flag"], False)