from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User, Group
from academic.models import major, university, group
from LessonsApp.models import lesson, lesson_class
from ..models import professor

class testProfessorViews(TestCase):

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
        data_1 = {
            "lesson_code":self.test_leeson_1,
            "professor_name":self.professor_obj,
            "university_location":self.uni_1,
            "group_name":self.test_group, 
            "class_start_time":"9:50", 
            "class_end_time":"11:50",
            "exam_date_time":"1404-12-06 20:00",
            "capacity":35, 
            "class_code":300, 
            "class_number":1002, 
        }
        data_2 = {
            "lesson_code":self.test_lesson_2,
            "professor_name":self.professor_obj,
            "university_location":self.uni_2,
            "group_name":self.test_group, 
            "class_start_time":"13:00", 
            "class_end_time":"16:00",
            "exam_date_time":"1404-12-06 18:00",
            "capacity":35, 
            "class_code":301, 
            "class_number":1002,
        }
        lesson_class.objects.create(**data_1)
        lesson_class.objects.create(**data_2)



    def test_professor_form_view(self):
        response = self.client.get(reverse("professor:register_professor"))
        self.assertRedirects(response, "/?next=/register-professor")
        self.assertTemplateNotUsed(response, "register_professor.html")

        # ? after login
        self.client.login(username="testprofessor", password="test")
        respone_after_login = self.client.get(reverse("professor:register_professor"))
        self.assertEqual(respone_after_login.status_code, 200)
        self.assertTemplateUsed(respone_after_login, "register_professor.html")



    def test_professor_profile_view(self):
        response = self.client.get(reverse("professor:professor_profile"))
        self.assertRedirects(response, "/?next=/professor/profile")
        self.assertTemplateNotUsed(response, "professor/profile.html")


        # ? after login
        self.client.login(username="testprofessor", password="test")
        response_after_login = self.client.get(reverse("professor:professor_profile"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "profile.html")

        temp_professor = response_after_login.wsgi_request.user.professor
        for uni in temp_professor.universities.all():
            self.assertContains(response_after_login, f"لیست دروس {uni.name}")
    


    def test_professor_lesson_list_view(self):
        response = self.client.get(reverse("professor:professor_lessons", kwargs={"p_code":"p_code", "u_code":"u_code"}))
        self.assertRedirects(response, "/?next=/professor/classes/p_code/u_code")
        self.assertTemplateNotUsed(response, "professor/professor_lesson_list.html")


        # ? after login
        self.client.login(username="testprofessor", password="test")
        response_after_login = self.client.get(reverse("professor:professor_profile"))
        self.assertEqual(response_after_login.status_code, 200)

        professor = response_after_login.wsgi_request.user.professor
        for i in professor.universities.all():
            response_after_getting_classes = self.client.get(reverse("professor:professor_lessons", kwargs={"p_code":str(professor.code), "u_code":str(i.code)}))
            self.assertEqual(response_after_getting_classes.status_code, 200)
            self.assertTemplateUsed(response_after_getting_classes, "professor_lesson_list.html")
            for j in professor.classes.filter(university_location=i):
                self.assertContains(response_after_getting_classes, f"{j.lesson_code}")
    


    def test_professor_lesson_details(self):
        response = self.client.get(reverse("professor:professor_lesson_detail", kwargs={"l_code":"l_code"}))
        self.assertRedirects(response, "/?next=/professor/lesson/details/l_code")
        self.assertTemplateNotUsed(response, "lesson_details.html")


        # ? after login
        self.client.login(username="testprofessor", password="test")
        response_after_login = self.client.get(reverse("professor:professor_profile"))
        self.assertEqual(response_after_login.status_code, 200)

        professor = response_after_login.wsgi_request.user.professor

        session = self.client.session
        session["p_code"] = professor.code
        session.save()
        for i in professor.classes.all():
            response_after_getting_class = self.client.get(reverse("professor:professor_lesson_detail", kwargs={"l_code":i.lesson_code.code}))
            self.assertContains(response_after_getting_class, f"لیست دانشجوهای روز {i.class_day}")
            self.assertTemplateUsed(response_after_getting_class,"professor_lesson_details.html")



    def test_grade_form_view(self):
        response = self.client.get(reverse("professor:grade", kwargs={"l_code":"l_code", "class_code":1234}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/?next=/professor/lesson/details/l_code/1234/submitting_grade")
        self.assertTemplateNotUsed(response,"submittingGrade.html")