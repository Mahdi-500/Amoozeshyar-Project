from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User, Group
from ..models import *

class generalViewsTests(TestCase):
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
        response = self.client.get(reverse("website:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Login.html")



    def test_main_view(self):
        response = self.client.get(reverse("website:main"))
        self.assertRedirects(response, "/?next=/main/")
        self.assertTemplateNotUsed(response, "main.html")
        
        # ? testing with admin privilages
        self.client.login(username="testadmin", password="test")
        response_after_admin_login = self.client.get(reverse("website:main"))
        self.assertTemplateUsed(response_after_admin_login, "main.html")
        self.assertContains(response_after_admin_login, "ثبت نام دانشجو")
        self.assertContains(response_after_admin_login, "ثبت نام استاد")
        self.assertContains(response_after_admin_login, "ثبت نام استاد")
        self.assertContains(response_after_admin_login, "ایجاد کلاس")
        self.assertContains(response_after_admin_login, "ایجاد درس")
        self.assertContains(response_after_admin_login,  "جتسجوی کلاس درس")

        # ? testing with professor privilages
        self.client.login(username="testprofessor", password="test")
        response_after_professor_login = self.client.get(reverse("website:main"))
        self.assertTemplateUsed(response_after_professor_login, "main.html")
        self.assertContains(response_after_professor_login, "پروفایل")


        # ? testing with student privilages
        self.client.login(username="teststudent", password="test")
        response_after_student_login = self.client.get(reverse("website:main"))
        self.assertTemplateUsed(response_after_student_login, "main.html")
        self.assertContains(response_after_student_login, "انتخاب واحد")
        self.assertContains(response_after_student_login, "جتسجوی کلاس درس")



    def test_lesson_form_view(self):
        response = self.client.get(reverse("website:create_lesson"))
        self.assertRedirects(response, "/?next=/create_lesson")
        self.assertTemplateNotUsed(response, "regiister_professor.html")

        # ? after login
        self.client.login(username="testadmin", password="test")
        response_after_login = self.client.get(reverse("website:create_lesson"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "register_professor.html")

        

    def test_lesson_class_form_view(self):
        response = self.client.get(reverse("website:lesson_class"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/create_class")
        self.assertTemplateNotUsed(response, "add_lesson_class.html")

        # ? after login
        self.client.login(username="testadmin", password="test")
        response_after_login = self.client.get(reverse("website:lesson_class"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "add_lesson_class.html")



class professorViewsTests(TestCase):

    def setUp(self):
        test_professor = User.objects.create_user(username="testprofessor", password="test")
        Group.objects.create(name="professor")
        test_professor.groups.add(Group.objects.get(name="professor"))

        # ? assigning uni to professor
        self.professor_obj = professor.objects.create(user=test_professor, first_name="test", last_name="test",
                                date_of_birth="1362-10-13", phone="09121234567")

        # ? creating major and group
        test_major = major.objects.create(name="test", code=200, capacity=100)
        self.test_group = group.objects.create(name="test", code=400)

        # ? creating lessons
        self.test_leeson_1 = lesson.objects.create(name="test1", code=100, unit=3)
        self.test_lesson_2 = lesson.objects.create(name="test2", code=101, unit=3)
        self.test_leeson_1.lesson_major.add(test_major)
        self.test_lesson_2.lesson_major.add(test_major)

        # ? creating the university
        self.uni_1 = university.objects.create(name="test1", code=1000, address="test address")
        self.uni_2 = university.objects.create(name="test2", code=1001, address="test address")
        self.professor_obj.universities.add(self.uni_1, self.uni_2)
        
        # ? creating lesson class
        lesson_class.objects.create(lesson_code=self.test_leeson_1, professor_name=self.professor_obj, university_location=self.uni_1, group_name=self.test_group, capacity=35, class_code=300, class_number=1002)
        lesson_class.objects.create(lesson_code=self.test_lesson_2, professor_name=self.professor_obj, university_location=self.uni_2, group_name=self.test_group, lesson_day="یک شنبه", capacity=35, class_code=301, class_number=1003)



    def test_professor_form_view(self):
        response = self.client.get(reverse("website:register_professor"))
        self.assertRedirects(response, "/?next=/register-professor")
        self.assertTemplateNotUsed(response, "register_professor.html")

        # ? after login
        self.client.login(username="testprofessor", password="test")
        respone_after_login = self.client.get(reverse("website:register_professor"))
        self.assertEqual(respone_after_login.status_code, 200)
        self.assertTemplateUsed(respone_after_login, "register_professor.html")



    def test_professor_profile_view(self):
        response = self.client.get(reverse("website:professor_profile"))
        self.assertRedirects(response, "/?next=/professor/profile")
        self.assertTemplateNotUsed(response, "professor/profile.html")


        # ? after login
        self.client.login(username="testprofessor", password="test")
        response_after_login = self.client.get(reverse("website:professor_profile"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "professor/profile.html")

        temp_professor = response_after_login.wsgi_request.user.professor
        for uni in temp_professor.universities.all():
            self.assertContains(response_after_login, f"لیست دروس {uni.name}")
    


    def test_professor_lesson_list_view(self):
        response = self.client.get(reverse("website:professor_lessons", kwargs={"p_code":"p_code", "u_code":"u_code"}))
        self.assertRedirects(response, "/?next=/professor/classes/p_code/u_code")
        self.assertTemplateNotUsed(response, "professor/professor_lesson_list.html")


        # ? after login
        self.client.login(username="testprofessor", password="test")
        response_after_login = self.client.get(reverse("website:professor_profile"))
        self.assertEqual(response_after_login.status_code, 200)

        professor = response_after_login.wsgi_request.user.professor
        for i in professor.universities.all():
            response_after_getting_classes = self.client.get(reverse("website:professor_lessons", kwargs={"p_code":str(professor.code), "u_code":str(i.code)}))
            self.assertEqual(response_after_getting_classes.status_code, 200)
            self.assertTemplateUsed(response_after_getting_classes, "professor/professor_lesson_list.html")
            for j in professor.classes.filter(university_location=i):
                self.assertContains(response_after_getting_classes, f"{j.lesson_code}")
    


    def test_professor_lesson_details(self):
        response = self.client.get(reverse("website:lesson_detail", kwargs={"l_code":"l_code"}))
        self.assertRedirects(response, "/?next=/professor/lesson/details/l_code")
        self.assertTemplateNotUsed(response, "lesson_details.html")


        # ? after login
        self.client.login(username="testprofessor", password="test")
        response_after_login = self.client.get(reverse("website:professor_profile"))
        self.assertEqual(response_after_login.status_code, 200)

        professor = response_after_login.wsgi_request.user.professor

        session = self.client.session
        session["p_code"] = professor.code
        session.save()
        for i in professor.classes.all():
            response_after_getting_class = self.client.get(reverse("website:lesson_detail", kwargs={"l_code":i.lesson_code.code}))
            self.assertContains(response_after_getting_class, f"لیست دانشجوهای روز {i.lesson_day}")
            self.assertTemplateUsed(response_after_getting_class,"lesson_details.html")



    def test_grade_form_view(self):
        response = self.client.get(reverse("website:grade", kwargs={"l_code":"l_code", "class_code":1234}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/professor/lesson/details/l_code/1234/submitting_grade")
        self.assertTemplateNotUsed(response,"submittingGrade.html")



class studentViewsTests(TestCase):

    def setUp(self):
        student = User.objects.create_user(username="teststudent", password="test")
        Group.objects.create(name="student")
        student.groups.add(Group.objects.get(name="student"))



    def test_student_form_view(self):
        response = self.client.get(reverse("website:register_student"))
        self.assertRedirects(response, "/?next=/register-student")
        self.assertTemplateNotUsed(response, "register_student.html")

        # ? after login
        self.client.login(username="teststudent", password="test")
        response_after_login = self.client.get(reverse("website:register_student"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "register_student.html")



    def test_lesson_search_view(self):
        response = self.client.get(reverse("website:lesson_search"))
        self.assertRedirects(response, "/?next=/search")
        self.assertTemplateNotUsed(response, "lesson_search_result.html")

        # ? after login
        self.client.login(username="teststudent", password="test")
        response_after_login = self.client.get(reverse("website:lesson_search"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "lesson_search_result.html")



    def test_choosing_lesson_form_view(self):
        response = self.client.get(reverse("website:choosing_lesson"))
        self.assertRedirects(response, "/?next=/choosing_lesson")
        self.assertTemplateNotUsed(response, "lesson_search_result.html")

        # ? after login
        self.client.login(username="teststudent", password="test")
        response_after_login = self.client.get(reverse("website:choosing_lesson"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed("lesson_search_result.htnl")
    


    def test_saving_chosen_lesson_view(self):
        response = self.client.get(reverse("website:save"))
        self.assertRedirects(response, "/?next=/saving")
        self.assertTemplateNotUsed("choosing_lesson.html")

        # ? after login
        self.client.login(username="teststudent", password="test")
        response_after_login = self.client.get(reverse("website:save"))
        self.assertRedirects(response_after_login, "/choosing_lesson")