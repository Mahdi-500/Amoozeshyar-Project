from django.urls import reverse
from django.test import TestCase
from unittest.mock import patch
from django_jalali.db.models import jdatetime
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from academic.models import major, university, group
from LessonsApp.models import lesson, lesson_class
from ProfessorsApp.models import professor, Grade
from ..models import student, student_choosing_lesson
from ..forms import StudentLessonSearchForm, semester as set_semester

class testStudentFormView(TestCase):
    def setUp(self):
        test_admin_user = User.objects.create_user(username="test_admin", password="test_pass")
        Group.objects.create(name="admin")
        test_admin_user.groups.add(Group.objects.get(name="admin"))



    def test_when_user_is_not_logged_in(self):
        response = self.client.get(reverse("student:register_student"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/?next=/register-student")
        self.assertTemplateUsed(response, "Login.html")



    def test_when_user_is_not_authorized(self):
        # ? create user
        test_student_user = User.objects.create_user(username="test_student", password="test_pass")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))

        self.client.login(username="test_student", password="test_pass")
        response = self.client.get(reverse("student:register_student"), follow=True)
        self.assertTemplateUsed(response, "forbidden.html")



    def test_with_GET_method(self):
        self.client.login(username="test_admin", password="test_pass")
        response = self.client.get(reverse("student:register_student"))
        self.assertTemplateUsed(response, "register_student.html")
        self.assertIn("form", response.context)



    def test_with_POST_method(self):
        self.client.login(username="test_admin", password="test_pass")
        # ? cretae university
        test_uni = university.objects.create(name="test", code=100)

        # ? creating major
        test_major = major.objects.create(name="test", code=200, capacity=200)

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")

        form_data = {
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1382-03-15",
            "student_id":"0123456789",
            "photo":photo,
            "mobile":"09121234567",
            "address":"test",
            "student_number":"405100200100",
            "major":test_major.pk,
            "university":test_uni.pk,
        }
        response = self.client.post(reverse("student:register_student"), data={**form_data}, format="multipart", follow=True)
        self.assertRedirects(response, reverse("academic:main"))
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "ثبت نام موفقیت آمیز بود")
        self.assertTemplateUsed(response, "main.html")
        self.assertTrue(student.objects.filter(student_number="405100200100").exists())
        self.assertTrue(Group.objects.filter(name="student").exists())
        self.assertEqual(student.objects.get(student_number="405100200100").user.groups.get().name, "student")



class testStudentLessonSearchForm(TestCase):
    def setUp(self):
        # ? creating admin
        test_admin = User.objects.create_user(username="test_admin", password="test_pass")
        test_group = Group.objects.create(name="admin")
        test_admin.groups.add(test_group)

        self.test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")

        Group.objects.create(name="test_professor")

        self.test_professor_user.groups.add(Group.objects.get(name="test_professor"))

        # ? creating university
        self.test_uni = university.objects.create(name="test", code=500, address="test")
        
        # ? creating major
        self.test_major = major.objects.create(name="test", code=100, capacity=1000)

        # ? creating lesson
        self.test_major_1 = major.objects.create(name="test1", code=101, capacity=200)

        self.test_lesson_obj = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        self.test_lesson_obj_2 = lesson.objects.create(name="test2", unit=4, unit_type=lesson.unit_type_choices.AMALI, 
                                            lesson_type=lesson.lesson_type_choices.PAYE)
        self.test_lesson_obj.lesson_major.add(self.test_major, self.test_major_1)
        self.test_lesson_obj_2.lesson_major.add(self.test_major, self.test_major_1)

        # ? creating professor
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        p_data = {
            "user":self.test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        self.test_professor_obj = professor.objects.create(**p_data)

        # ? creating group
        self.test_group = group.objects.create(name="test", code=500)

        # ? creating class
        class_data_1 = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }

        class_data_2 = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"18:00:00",
            "class_end_time":"20:00:00",
            "exam_date_time":"1405-03-12 13:00",
            "capacity":35,
            "class_code":301,
            "class_number":1212,
            "semester":4042,
        }

        class_data_3 = {
            "lesson_code":self.test_lesson_obj_2,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":302,
            "class_number":1211,
            "semester":4042,
        }

        class_data_4 = {
            "lesson_code":self.test_lesson_obj_2,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"18:00:00",
            "class_end_time":"20:00:00",
            "exam_date_time":"1405-03-12 13:00",
            "capacity":35,
            "class_code":303,
            "class_number":1210,
            "semester":4042,
        }
        self.lesson_class_obj_1 = lesson_class.objects.create(**class_data_1)
        self.lesson_class_obj_2 = lesson_class.objects.create(**class_data_2)
        self.lesson_class_obj_3 = lesson_class.objects.create(**class_data_3)
        self.lesson_class_obj_4 = lesson_class.objects.create(**class_data_4)



    def test_with_GET_method(self):
        self.client.login(username="test_admin", password="test_pass")
        response = self.client.get(reverse("student:lesson_search"))
        self.assertTemplateUsed(response, "lesson_search_result.html")
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("flag", response.context)
        self.assertEqual(response.context["flag"], False)
        self.assertIsInstance(response.context["form"], StudentLessonSearchForm)



    def test_context_keys_using_lesson_code_with_POST_method(self):
        self.client.login(username="test_admin", password="test_pass")
        search_data = {
            "query_lesson_code":self.test_lesson_obj.code,
            "query_lesson_name":"",
            "query_unit_type":"",
            "query_lesson_type":"",
            "query_lesson_semester":4042
        }
        response = self.client.post(reverse("student:lesson_search"), data={**search_data})
        self.assertIn("result", response.context)
        self.assertIn("form", response.context)
        self.assertIn("flag", response.context)
        self.assertTemplateUsed("lesson_search_result.html")



    def test_context_values_using_lesson_code_with_POST_method(self):
        self.client.login(username="test_admin", password="test_pass")
        search_data = {
            "query_lesson_code":self.test_lesson_obj.code,
            "query_lesson_name":"",
            "query_unit_type":"",
            "query_lesson_type":"",
            "query_lesson_semester":4042
        }
        response = self.client.post(reverse("student:lesson_search"), data={**search_data})
        self.assertIn(self.lesson_class_obj_1, response.context["result"])
        self.assertIn(self.lesson_class_obj_2, response.context["result"])
        self.assertIsInstance(response.context["form"], StudentLessonSearchForm)
        self.assertEqual(response.context["flag"], True)



    def test_context_values_using_lesson_name_with_POST_method(self):
        self.client.login(username="test_admin", password="test_pass")
        search_data = {
            "query_lesson_code":"",
            "query_lesson_name":self.test_lesson_obj_2.name,
            "query_unit_type":"",
            "query_lesson_type":"",
            "query_lesson_semester":4042
        }
        response = self.client.post(reverse("student:lesson_search"), data={**search_data})
        self.assertIn(self.lesson_class_obj_3, response.context["result"])
        self.assertIn(self.lesson_class_obj_4, response.context["result"])
        self.assertIsInstance(response.context["form"], StudentLessonSearchForm)
        self.assertEqual(response.context["flag"], True)



    def test_context_values_using_unit_type_with_POST_method(self):
        self.client.login(username="test_admin", password="test_pass")
        search_data = {
            "query_lesson_code":"",
            "query_lesson_name":"",
            "query_unit_type":lesson.unit_type_choices.NAZARI,
            "query_lesson_type":"",
            "query_lesson_semester":4042
        }
        response = self.client.post(reverse("student:lesson_search"), data={**search_data})
        self.assertIn(self.lesson_class_obj_1, response.context["result"])
        self.assertIn(self.lesson_class_obj_2, response.context["result"])
        self.assertIsInstance(response.context["form"], StudentLessonSearchForm)
        self.assertEqual(response.context["flag"], True)



    def test_context_values_using_lesson_type_with_POST_method(self):
        self.client.login(username="test_admin", password="test_pass")
        search_data = {
            "query_lesson_code":"",
            "query_lesson_name":"",
            "query_unit_type":"",
            "query_lesson_type":lesson.lesson_type_choices.PAYE,
            "query_lesson_semester":4042
        }
        response = self.client.post(reverse("student:lesson_search"), data={**search_data})
        self.assertIn(self.lesson_class_obj_3, response.context["result"])
        self.assertIn(self.lesson_class_obj_4, response.context["result"])
        self.assertIsInstance(response.context["form"], StudentLessonSearchForm)
        self.assertEqual(response.context["flag"], True)



    def test_context_values_with_no_search_filters_using_POST_method(self):
        self.client.login(username="test_admin", password="test_pass")
        search_data = {
            "query_lesson_code":"",
            "query_lesson_name":"",
            "query_unit_type":"",
            "query_lesson_type":"",
            "query_lesson_semester":4042
        }
        response = self.client.post(reverse("student:lesson_search"), data={**search_data})
        self.assertIn(self.lesson_class_obj_1, response.context["result"])
        self.assertIn(self.lesson_class_obj_2, response.context["result"])
        self.assertIn(self.lesson_class_obj_3, response.context["result"])
        self.assertIn(self.lesson_class_obj_4, response.context["result"])
        self.assertIsInstance(response.context["form"], StudentLessonSearchForm)
        self.assertEqual(response.context["flag"], True)



class testStudentViews(TestCase):
    def setUp(self):
        test_student_user = User.objects.create_user(username="test_student", password="test_pass")
        test_admin_user = User.objects.create_user(username="test_admin", password="test_pass")

        Group.objects.create(name="student")
        Group.objects.create(name="admin")

        test_student_user.groups.add(Group.objects.get(name="student"))
        test_admin_user.groups.add(Group.objects.get(name="admin"))



    def test_lesson_obj_search_view(self):
        response = self.client.get(reverse("student:lesson_search"))
        self.assertRedirects(response, "/?next=/search")
        self.assertTemplateNotUsed(response, "lesson_search_result.html")

        # ? after login
        self.client.login(username="test_student", password="test_pass")
        response_after_login = self.client.get(reverse("student:lesson_search"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed(response_after_login, "lesson_search_result.html")



class testChoosingLessonView(TestCase):
    def setUp(self):
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        self.test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")

        Group.objects.create(name="student")
        Group.objects.create(name="test_professor")

        test_student_user.groups.add(Group.objects.get(name="student"))
        self.test_professor_user.groups.add(Group.objects.get(name="test_professor"))

        # ? creating university
        self.test_uni = university.objects.create(name="test", code=500, address="test")
        
        # ? creating major
        self.test_major = major.objects.create(name="test", code=100, capacity=1000)


        # ? creating student
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":self.test_major,
            "university":self.test_uni,
        }

        self.test_student_obj = student.objects.create(**data)



    def test_login_required_decorator(self):
        response = self.client.get(reverse("student:choosing_lesson"), follow=True)
        self.assertRedirects(response, "/?next=/choosing_lesson")
        self.assertTemplateUsed(response, "Login.html")



    def test_is_user_authorized_decorator(self):
        # ? login with wrong role
        temp_user = User.objects.create_user(username="temp_user", password="test_pass")
        temp_group = Group.objects.get(name="test_professor")
        temp_user.groups.add(temp_group)
        self.client.login(username="temp_user", password="test_pass")
        response_after_login = self.client.get(reverse("student:choosing_lesson"))
        self.assertTemplateUsed(response_after_login, "forbidden.html")
        self.assertContains(response_after_login, "شما اجازه دسترسی به این بخش را ندارید")

        # ? after login
        self.client.login(username=self.test_student_obj.student_number, password=str(self.test_student_obj.date_of_birth.year))
        
        ## ? setting session
        session = self.client.session
        session['chosen_classes'] = []
        session.save()

        response_after_login = self.client.get(reverse("student:choosing_lesson"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed("choosing_lesson.html")
    


    def test_with_other_student_status(self):
        # ? change status
        self.test_student_obj.status = "فارغ"
        self.test_student_obj.save()

        self.client.login(username="123456789123", password="1382")
        response_after_login = self.client.get(reverse("student:choosing_lesson"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed("forbidden.html")
    


    def test_when_student_status_is_studying_GET_returns_correct_context(self):  
        self.client.login(username="123456789123", password="1382")
        session = self.client.session
        session["chosen_classes"] = []
        session.save()
        response_after_login = self.client.get(reverse("student:choosing_lesson"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed("choosing_lesson.html")

        excepted_keys = ["form_searching", "chosen_classes", "max_unit", "sum_of_the_chosen_units"]
        for i in excepted_keys:
            self.assertIn(i, response_after_login.context.keys())
        self.assertIsInstance(response_after_login.context["form_searching"], StudentLessonSearchForm)

        self.assertEqual(response_after_login.context["chosen_classes"], {})    # ? student didn't choose any lesson yet



    def test_when_student_status_is_studying_POST_returns_correct_context(self):
        self.client.login(username="123456789123", password="1382")
        session = self.client.session
        session["chosen_classes"] = []
        session.save()

        # ? creating lesson
        self.test_major_1 = major.objects.create(name="test1", code=101, capacity=200)

        self.test_lesson_obj = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        self.test_lesson_obj_2 = lesson.objects.create(name="test2", unit=4, unit_type=lesson.unit_type_choices.AMALI, 
                                            lesson_type=lesson.lesson_type_choices.PAYE)
        self.test_lesson_obj.lesson_major.add(self.test_major, self.test_major_1)
        self.test_lesson_obj_2.lesson_major.add(self.test_major, self.test_major_1)

        # ? creating professor
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        p_data = {
            "user":self.test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        self.test_professor_obj = professor.objects.create(**p_data)

        # ? creating group
        self.test_group = group.objects.create(name="test", code=500)

        # ? creating class
        class_data_1 = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }

        class_data_2 = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"18:00:00",
            "class_end_time":"20:00:00",
            "exam_date_time":"1405-03-12 13:00",
            "capacity":35,
            "class_code":301,
            "class_number":1212,
            "semester":4042,
        }
        class_obj_1 = lesson_class.objects.create(**class_data_1)
        class_obj_2 = lesson_class.objects.create(**class_data_2)

        form_data = {
            "query_lesson_code":self.test_lesson_obj.code,
            "query_lesson_semester":"4042",
        }

        reponse = self.client.post(reverse("student:choosing_lesson"), data={**form_data})
        self.assertEqual(reponse.status_code, 200)
        self.assertTemplateUsed("choosing_lesson.html")
        excepted_keys = ["form_searching", "available_classes", "flag", "chosen_classes", "max_unit", "sum_of_the_chosen_units"]
        for i in excepted_keys:
            self.assertIn(i, reponse.context.keys())
        available_classes = reponse.context["available_classes"]

        self.assertIn([class_obj_1.id, class_obj_1.lesson_code.name, class_obj_1.professor_name, 
                        class_obj_1.lesson_code.code, str(class_obj_1.class_day), 
                        f"{class_obj_1.class_end_time} تا {class_obj_1.class_start_time}"], available_classes.values())
        
        self.assertIn([class_obj_2.id, class_obj_2.lesson_code.name, class_obj_2.professor_name, 
                        class_obj_2.lesson_code.code, str(class_obj_2.class_day),
                        f"{class_obj_2.class_end_time} تا {class_obj_2.class_start_time}"], available_classes.values())

    

class testTemporarelySavingChosenLessonView(TestCase):
    def setUp(self):
        session = self.client.session
        session["semester"] = 4042
        session["chosen_classes"] = []
        session.save()
        # ? create major
        self.test_major= major.objects.create(name="test1", code=101, capacity=200)

        # ? creating university
        self.test_uni = university.objects.create(name="test", code=500, address="test")

        # ? creating lesson
        self.test_lesson_obj = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        self.test_lesson_obj.lesson_major.add(self.test_major)
        
        # ? creating group
        self.test_group = group.objects.create(name="test", code=500)

        # ? creating professor
        self.test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        p_data = {
            "user":self.test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        self.test_professor_obj = professor.objects.create(**p_data)

        # ? creating student
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))

        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":self.test_major,
            "university":self.test_uni,
        }

        self.test_student_obj = student.objects.create(**data)
        


    def test_login_required_decorator(self):
        response = self.client.get(reverse("student:pre_save"), follow=True)
        self.assertRedirects(response, "/?next=/pre-saving")
        self.assertTemplateUsed(response, "Login.html")



    def test_is_user_authorized_decorator(self):
        # ? login with wrong role
        temp_user = User.objects.create_user(username="temp_user", password="test_pass")
        Group.objects.create(name="test_professor")
        temp_group = Group.objects.get(name="test_professor")
        temp_user.groups.add(temp_group)
        self.client.login(username="temp_user", password="test_pass")
        response_after_login = self.client.get(reverse("student:pre_save"))
        self.assertTemplateUsed(response_after_login, "forbidden.html")
        self.assertContains(response_after_login, "شما اجازه دسترسی به این بخش را ندارید")

        # ? after login
        self.client.login(username=self.test_student_obj.student_number, password=str(self.test_student_obj.date_of_birth.year))
        
        ## ? setting session
        session = self.client.session
        session['chosen_classes'] = []
        session.save()

        response_after_login = self.client.get(reverse("student:pre_save"), follow=True)
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed("choosing_lesson.html")


    
    def test_duplicate_lesson_in_current_semester(self):
        # ? creating class
        class_data = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        class_obj = lesson_class.objects.create(**class_data)

        # ? adding to chosen lessons
        data = {
            "student_name":self.test_student_obj,
            "chosen_class":class_obj,
            "semester":self.client.session["semester"]
        }
        student_choosing_lesson.objects.create(**data)

        self.client.login(username="123456789123", password="1382")
        response = self.client.post(reverse("student:pre_save"), data={"chosen_class":class_obj.id}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "درس تکراری مجاز نیست")
        self.assertNotEqual(len(student_choosing_lesson.objects.filter(**data)), 2)
        self.assertRedirects(response, reverse("student:choosing_lesson"))



    def test_check_previous_semesters_find_duplicate_lesson(self):
        # ? creating class for previous semester
        class_data = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4031,
        }
        class_obj = lesson_class.objects.create(**class_data)

        # ? adding to chosen lessons
        data = {
            "student_name":self.test_student_obj,
            "chosen_class":class_obj,
            "semester":4031
        }
        student_choosing_lesson.objects.create(**data)

        grade_data = {
            "student_name":self.test_student_obj,
            "lesson_name":class_obj,
            "mark":17
        }
        Grade.objects.create(**grade_data)

        # ? creating class for current semester
        temp_class_data = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        temp_class_obj = lesson_class.objects.create(**temp_class_data)

        self.client.login(username="123456789123", password="1382")
        response = self.client.post(reverse("student:pre_save"), data={"chosen_class":class_obj.id}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "این درس را قبلا برداشته اید")

        filter_options = {
            "student_name":self.test_student_obj,
            "chosen_class":temp_class_obj,
            "semester":4042
        }
        self.assertFalse(student_choosing_lesson.objects.filter(**filter_options).exists())
        self.assertRedirects(response, reverse("student:choosing_lesson"))



    def test_if_student_passed_the_requirements(self):
        # ? creating the lesson which is the required lesson for test_lesson_obj
        r_lesson_data = {
            "name":"test2",
            "unit":4,
            "unit_type":lesson.unit_type_choices.NAZARI,
            "lesson_type":lesson.lesson_type_choices.TAKHASOSI
        }
        r_lesson = lesson.objects.create(**r_lesson_data)

        # ? adding the required lesson to main lesson
        self.test_lesson_obj.pishniaz.add(r_lesson)
        self.test_lesson_obj.save()

        # ? creating class for main lesson
        class_data = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        class_obj = lesson_class.objects.create(**class_data)

        self.client.login(username="123456789123", password="1382")
        response = self.client.post(reverse("student:pre_save"), data={"chosen_class":class_obj.id}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "ابتدا باید پیش نیاز درس را قبول بشوید")

        filter_options = {
            "student_name":self.test_student_obj,
            "chosen_class":class_obj,
            "semester":4042
        }
        self.assertFalse(student_choosing_lesson.objects.filter(**filter_options).exists())
        self.assertRedirects(response, reverse("student:choosing_lesson"))


    @patch('StudentsApp.views.check_overall_unit_picked')
    @patch('StudentsApp.views.maximum_unit_allowed')
    def test_not_exceed_max_unit_allowed(self, mock_max_unit, mock_is_maximum_units_limit_passed):

        mock_max_unit.return_value = 20
        mock_is_maximum_units_limit_passed.return_value = True

        # ? creating class for the lesson
        class_data = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        class_obj = lesson_class.objects.create(**class_data)

        self.client.login(username="123456789123", password="1382")
        response = self.client.post(reverse("student:pre_save"), data={"chosen_class":class_obj.id}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, f"تعداد واحد انتخابی از سقف تعداد واحد مجاز ({mock_max_unit.return_value}) بیشتر است")
        self.assertRedirects(response, reverse("student:choosing_lesson"))
    


    def test_successful_choosing(self):
        # ? creating class for the lesson
        class_data = {
            "lesson_code":self.test_lesson_obj,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        class_obj = lesson_class.objects.create(**class_data)

        self.client.login(username="123456789123", password="1382")
        response = self.client.post(reverse("student:pre_save"), data={"chosen_class":class_obj.id}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "درس با موفقیت انتخاب شد")
        self.assertRedirects(response, reverse("student:choosing_lesson"))



class testChoosingLessonActions(TestCase):
    def test_submit_chosen_lessons(self):
        # ? create major
        test_major= major.objects.create(name="test1", code=101, capacity=200)

        # ? creating university
        test_uni = university.objects.create(name="test", code=500, address="test")

        # ? creating lesson
        test_lesson_obj = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj.lesson_major.add(test_major)
        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        # ? creating professor
        test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        p_data = {
            "user":test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        test_professor_obj = professor.objects.create(**p_data)

        # ? creating student
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))

        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":test_major,
            "university":test_uni,
        }
        test_student_obj = student.objects.create(**data)

        # ? creating class for the lesson
        class_data = {
            "lesson_code":test_lesson_obj,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        test_class_obj = lesson_class.objects.create(**class_data)

        session = self.client.session
        session["semester"] = 4042
        session["chosen_classes"] = [test_class_obj.id]
        session.save()

        self.client.login(username='123456789123', password="1382")
        response = self.client.get(reverse("student:submit"), follow=True)
        message = list(response.context['messages'])[0].message
        self.assertEqual(message, "درس های انتخابی با موفقیت ذخیره شدند")
        self.assertEqual(response.status_code, 200)
        class_info = lesson_class.objects.get(id=self.client.session["chosen_classes"][0])
        self.assertTrue(student_choosing_lesson.objects.filter(student_name=test_student_obj,
                                                                chosen_class=class_info,
                                                                semester=self.client.session["semester"]).exists())
        self.assertRedirects(response, reverse("student:choosing_lesson"))

    
    
    def test_login_required_decorator(self):
        response = self.client.get(reverse("student:submit"), follow=True)
        self.assertRedirects(response, "/?next=/submiting")
        self.assertTemplateUsed(response, "Login.html")



    def test_is_user_authorized_decorator(self):
        # ? create major
        test_major= major.objects.create(name="test1", code=101, capacity=200)

        # ? creating university
        test_uni = university.objects.create(name="test", code=500, address="test")
            
        # ? creating student
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":test_major,
            "university":test_uni,
        }
        test_student_obj = student.objects.create(**data)

        # ? login with wrong role
        temp_user = User.objects.create_user(username="temp_user", password="test_pass")
        Group.objects.create(name="test_professor")
        temp_group = Group.objects.get(name="test_professor")
        temp_user.groups.add(temp_group)
        self.client.login(username="temp_user", password="test_pass")
        response_after_login = self.client.get(reverse("student:submit"))
        self.assertTemplateUsed(response_after_login, "forbidden.html")
        self.assertContains(response_after_login, "شما اجازه دسترسی به این بخش را ندارید")

        # ? after login
        self.client.login(username=test_student_obj.student_number, password=str(test_student_obj.date_of_birth.year))
        
        ## ? setting session
        session = self.client.session
        session['chosen_classes'] = []
        session.save()

        response_after_login = self.client.get(reverse("student:submit"), follow=True)
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed("choosing_lesson.html")



    def test_delete_choesn_lesson(self):
        # ? create major
        test_major= major.objects.create(name="test1", code=101, capacity=200)

        # ? creating university
        test_uni = university.objects.create(name="test", code=500, address="test")

        # ? creating lesson
        test_lesson_obj = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj.lesson_major.add(test_major)
        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        # ? creating professor
        test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        p_data = {
            "user":test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        test_professor_obj = professor.objects.create(**p_data)

        # ? creating student
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))

        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":test_major,
            "university":test_uni,
        }

        test_student_obj = student.objects.create(**data)

        # ? creating class for the lesson
        class_data_1 = {
            "lesson_code":test_lesson_obj,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        test_class_obj_1 = lesson_class.objects.create(**class_data_1)

        class_data_2 = {
            "lesson_code":test_lesson_obj,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"17:45:00",
            "class_end_time":"19:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":301,
            "class_number":1212,
            "semester":4042,
        }
        test_class_obj_2 = lesson_class.objects.create(**class_data_2)

        session = self.client.session
        session['semester'] = 4042
        session['chosen_classes'] = [test_class_obj_1.id, test_class_obj_2.id]
        session.save()

        # ? creating student choosing lesson objects
        student_choosing_lesson.objects.create(student_name=test_student_obj,
                                                                chosen_class=test_class_obj_1,
                                                                semester=self.client.session["semester"])
        student_choosing_lesson.objects.create(student_name=test_student_obj,
                                                                chosen_class=test_class_obj_2,
                                                                semester=self.client.session["semester"])
        
        self.client.login(username='123456789123', password="1382")
        response = self.client.get(reverse("student:delete_lesson", kwargs={"lesson_class_id":test_class_obj_1.id}), follow=True)
        message = list(response.context["messages"])[0].message
        self.assertFalse(student_choosing_lesson.objects.filter(student_name=test_student_obj,
                                                                chosen_class=test_class_obj_1,
                                                                semester=self.client.session["semester"]).exists())
        self.assertNotIn(test_class_obj_1.id, self.client.session["chosen_classes"])
        self.assertEqual(message, "درس با موفقیت حذف شد")
        self.assertRedirects(response, reverse("student:choosing_lesson"))



class testStudentReportView(TestCase):
    def setUp(self):
        # ? create major
        self.test_major= major.objects.create(name="test1", code=101, capacity=200)

        # ? creating university
        self.test_uni = university.objects.create(name="test", code=500, address="test")

        # ? creating student
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":self.test_major,
            "university":self.test_uni,
        }
        self.test_student_obj = student.objects.create(**data)

    def test_context_when_student_has_no_classes(self):
        self.client.login(username="123456789123", password="1382")
        response = self.client.get(reverse("student:student_report"))
        expected_context_keys = ["lesson_report", "semester_status", "lesson_type_status", "overall_average", "overall_units"]
        for i in expected_context_keys:
            self.assertIn(i, response.context.keys())
        self.assertEqual(response.context["lesson_report"], {})
        self.assertEqual(response.context["semester_status"], {})
        self.assertEqual(response.context["lesson_type_status"], {"اصلی":0, "پایه":0, "عمومی":0, "تخصصی":0, "اختیاری":0,})
        self.assertEqual(response.context["overall_average"], 0)
        self.assertEqual(response.context["overall_units"], 0)



    def test_context_when_student_has_class_but_no_grades(self):
        # ? creating lessons
        test_lesson_obj_1 = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj_1.lesson_major.add(self.test_major)

        test_lesson_obj_2 = lesson.objects.create(name="test2", unit=4, unit_type=lesson.unit_type_choices.NAZARI_AMALI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj_2.lesson_major.add(self.test_major)

        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        # ? creating professor
        test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        p_data = {
            "user":test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        test_professor_obj = professor.objects.create(**p_data)
        # ? creating class for the lesson
        class_data_1 = {
            "lesson_code":test_lesson_obj_1,
            "professor_name":test_professor_obj,
            "university_location":self.test_uni,
            "group_name":test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        test_class_obj_1 = lesson_class.objects.create(**class_data_1)

        class_data_2 = {
            "lesson_code":test_lesson_obj_2,
            "professor_name":test_professor_obj,
            "university_location":self.test_uni,
            "group_name":test_group,
            "class_start_time":"17:45:00",
            "class_end_time":"19:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":301,
            "class_number":1212,
            "semester":4042,
        }
        test_class_obj_2 = lesson_class.objects.create(**class_data_2)

        # ? assigning classes to the student
        assigned_class_obj_1 = student_choosing_lesson.objects.create(
            student_name=self.test_student_obj,
            chosen_class=test_class_obj_1,
            semester=4042
        )
        assigned_class_obj_2 = student_choosing_lesson.objects.create(
            student_name=self.test_student_obj,
            chosen_class=test_class_obj_2,
            semester=4042
        )

        self.client.login(username="123456789123", password="1382")
        response = self.client.get(reverse("student:student_report"))
        self.assertEqual(response.context["lesson_report"][4042], [(assigned_class_obj_1, "No mark yet"), (assigned_class_obj_2, "No mark yet")])
        self.assertEqual(response.context["semester_status"][4042], [(0, 7, 0.0)])
        self.assertEqual(response.context["lesson_type_status"], {"اصلی":0, "پایه":0, "عمومی":0, "تخصصی":7, "اختیاری":0})
        self.assertEqual(response.context["overall_average"], 0)
        self.assertEqual(response.context["overall_units"], 7)



    def test_context_when_student_has_class_with_grades(self):
        # ? creating lessons
        test_lesson_obj_1 = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj_1.lesson_major.add(self.test_major)

        test_lesson_obj_2 = lesson.objects.create(name="test2", unit=4, unit_type=lesson.unit_type_choices.NAZARI_AMALI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj_2.lesson_major.add(self.test_major)

        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        # ? creating professor
        test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        p_data = {
            "user":test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        test_professor_obj = professor.objects.create(**p_data)
        # ? creating class for the lesson
        class_data_1 = {
            "lesson_code":test_lesson_obj_1,
            "professor_name":test_professor_obj,
            "university_location":self.test_uni,
            "group_name":test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4042,
        }
        test_class_obj_1 = lesson_class.objects.create(**class_data_1)

        class_data_2 = {
            "lesson_code":test_lesson_obj_2,
            "professor_name":test_professor_obj,
            "university_location":self.test_uni,
            "group_name":test_group,
            "class_start_time":"17:45:00",
            "class_end_time":"19:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":301,
            "class_number":1212,
            "semester":4042,
        }
        test_class_obj_2 = lesson_class.objects.create(**class_data_2)

        # ? assigning classes to the student
        assigned_class_obj_1 = student_choosing_lesson.objects.create(
            student_name=self.test_student_obj,
            chosen_class=test_class_obj_1,
            semester=4042
        )
        assigned_class_obj_2 = student_choosing_lesson.objects.create(
            student_name=self.test_student_obj,
            chosen_class=test_class_obj_2,
            semester=4042
        )
        
        # ? assigning marks
        Grade.objects.create(
            student_name=self.test_student_obj,
            lesson_name=test_class_obj_1,
            mark=20
        )
        Grade.objects.create(
            student_name=self.test_student_obj,
            lesson_name=test_class_obj_2,
            mark=17.5
        )

        self.client.login(username="123456789123", password="1382")
        response = self.client.get(reverse("student:student_report"))
        self.assertEqual(response.context["lesson_report"][4042], [(assigned_class_obj_1, 20), (assigned_class_obj_2, 17.5)])
        from decimal import Decimal
        self.assertEqual(response.context["semester_status"][4042], [(Decimal('130.00'), 7, Decimal('18.57'))])
        self.assertEqual(response.context["lesson_type_status"], {"اصلی":0, "پایه":0, "عمومی":0, "تخصصی":7, "اختیاری":0})
        self.assertEqual(response.context["overall_average"], Decimal('18.57'))
        self.assertEqual(response.context["overall_units"], 7)



    def test_login_required_decorator(self):
        response = self.client.get(reverse("student:student_report"), follow=True)
        self.assertRedirects(response, "/?next=/student_report")
        self.assertTemplateUsed(response, "Login.html")



    def test_is_user_authorized_decorator(self):
        # ? login with wrong role
        temp_user = User.objects.create_user(username="temp_user", password="test_pass")
        Group.objects.create(name="test_professor")
        temp_group = Group.objects.get(name="test_professor")
        temp_user.groups.add(temp_group)
        self.client.login(username="temp_user", password="test_pass")
        response_after_login = self.client.get(reverse("student:student_report"))
        self.assertTemplateUsed(response_after_login, "forbidden.html")
        self.assertContains(response_after_login, "شما اجازه دسترسی به این بخش را ندارید")

        # ? after login
        self.client.login(username=self.test_student_obj.student_number, password=str(self.test_student_obj.date_of_birth.year))
        
        ## ? setting session
        session = self.client.session
        session['chosen_classes'] = []
        session.save()

        response_after_login = self.client.get(reverse("student:student_report"))
        self.assertEqual(response_after_login.status_code, 200)
        self.assertTemplateUsed("student_report.html")



from ..views import maximum_unit_allowed
class testMaximumUnitAllowedFunction(TestCase):
    def setUp(self):
        # ? create major
        self.test_major= major.objects.create(name="test1", code=101, capacity=200)

        # ? creating university
        self.test_uni = university.objects.create(name="test", code=500, address="test")

        # ? creating student
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":self.test_major,
            "university":self.test_uni,
        }
        self.test_student_obj = student.objects.create(**data)

        # ? creating lessons
        test_lesson_obj_1 = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj_1.lesson_major.add(self.test_major)

        test_lesson_obj_2 = lesson.objects.create(name="test2", unit=4, unit_type=lesson.unit_type_choices.NAZARI_AMALI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj_2.lesson_major.add(self.test_major)

        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        # ? creating professor
        test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")

        p_data = {
            "user":test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        test_professor_obj = professor.objects.create(**p_data)

        # ? creating class for the lesson
        class_data_1 = {
            "lesson_code":test_lesson_obj_1,
            "professor_name":test_professor_obj,
            "university_location":self.test_uni,
            "group_name":test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4032,
        }
        test_class_obj_1 = lesson_class.objects.create(**class_data_1)

        class_data_2 = {
            "lesson_code":test_lesson_obj_2,
            "professor_name":test_professor_obj,
            "university_location":self.test_uni,
            "group_name":test_group,
            "class_start_time":"17:45:00",
            "class_end_time":"19:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":301,
            "class_number":1212,
            "semester":4032,
        }
        test_class_obj_2 = lesson_class.objects.create(**class_data_2)

        # ? assigning classes to the student
        self.assigned_class_obj_1 = student_choosing_lesson.objects.create(
            student_name=self.test_student_obj,
            chosen_class=test_class_obj_1,
            semester=4032
        )
        self.assigned_class_obj_2 = student_choosing_lesson.objects.create(
            student_name=self.test_student_obj,
            chosen_class=test_class_obj_2,
            semester=4032
        )
        
        # ? assigning marks
        self.assigned_grade_1 = Grade.objects.create(
            student_name=self.test_student_obj,
            lesson_name=test_class_obj_1,
            mark=20
        )
        self.assigned_grade_2 = Grade.objects.create(
            student_name=self.test_student_obj,
            lesson_name=test_class_obj_2,
            mark=17.5
        )


    @patch("StudentsApp.views.set_semester")
    def test_when_it_is_summer(self, mock):
        mock.return_value = '4043'
        self.assertEqual(maximum_unit_allowed(self.test_student_obj), 8)

    

    @patch("StudentsApp.views.set_semester")
    def test_with_normal_average_score(self, mock):
        mock.return_value = '4041'
        self.assigned_grade_1.mark = 15
        self.assigned_grade_1.save()
        self.assertEqual(maximum_unit_allowed(self.test_student_obj), 20)



    @patch("StudentsApp.views.set_semester")
    def test_with_top_average_score(self, mock):
        mock.return_value = '4041'
        self.assertEqual(maximum_unit_allowed(self.test_student_obj), 24)



    @patch("StudentsApp.views.set_semester")
    def test_with_the_worst_average_score(self, mock):
        mock.return_value = '4041'
        self.assigned_grade_1.mark = 10
        self.assigned_grade_2.mark = 10
        self.assigned_grade_1.save()
        self.assigned_grade_2.save()
        self.assertEqual(maximum_unit_allowed(self.test_student_obj), 12)



    @patch("StudentsApp.views.set_semester")
    def test_with_student_not_having_any_class_yet(self, mock):
        mock.return_value = '4041'
        self.assigned_class_obj_1.delete()
        self.assigned_class_obj_2.delete()

        self.assertEqual(maximum_unit_allowed(self.test_student_obj), -1)



from ..views import check_overall_unit_picked
class testCheckOverallUnitPickedFunction(TestCase):
    def setUp(self):
        # ? create major
        self.test_major= major.objects.create(name="test1", code=101, capacity=200)

        # ? creating university
        self.test_uni = university.objects.create(name="test", code=500, address="test")

        # ? creating student
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":self.test_major,
            "university":self.test_uni,
        }
        student.objects.create(**data)

        session = self.client.session
        session["chosen_classes"] = []
        session.save()

        self.client.login(username="123456789123", password="1382")
        response = self.client.get(reverse("student:choosing_lesson"))
        self.request = response.wsgi_request

        # ? creating lessons
        test_lesson_obj_1 = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj_1.lesson_major.add(self.test_major)

        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        # ? creating professor
        test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")

        p_data = {
            "user":test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        test_professor_obj = professor.objects.create(**p_data)

        # ? creating class for the lesson
        class_data_1 = {
            "lesson_code":test_lesson_obj_1,
            "professor_name":test_professor_obj,
            "university_location":self.test_uni,
            "group_name":test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4032,
        }
        self.test_class_obj_1 = lesson_class.objects.create(**class_data_1)



    def test_with_chosen_class_being_empty(self):
        self.assertFalse(check_overall_unit_picked(request=self.request, max_unit=20, chosen_class=self.test_class_obj_1))



    def test_when_it_does_not_exceed(self):
        self.request.session["chosen_classes"] = [self.test_class_obj_1.id]
        self.assertFalse(check_overall_unit_picked(request=self.request, max_unit=10, chosen_class=self.test_class_obj_1))



    def test_when_exceeds(self):
        self.request.session["chosen_classes"] = [self.test_class_obj_1.id]
        self.assertTrue(check_overall_unit_picked(request=self.request, max_unit=3, chosen_class=self.test_class_obj_1))



from ..views import check_lesson_requirements_status
class testCheckLessonRequirementsStatus(TestCase):
    def setUp(self):
        # ? create major
        test_major= major.objects.create(name="test1", code=101, capacity=200)

        # ? creating university
        test_uni = university.objects.create(name="test", code=500, address="test")

        # ? creating student
        test_student_user = User.objects.create_user(username="123456789123", password="1382")
        Group.objects.create(name="student")
        test_student_user.groups.add(Group.objects.get(name="student"))

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        data = {
            "user_id":test_student_user.id,
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "student_number":"123456789123",
            "major":test_major,
            "university":test_uni,
        }
        self.test_student_obj = student.objects.create(**data)
        
        # ? creating lessons
        test_lesson_obj_1 = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        test_lesson_obj_1.lesson_major.add(test_major)

        self.test_lesson_obj_2 = lesson.objects.create(name="test2", unit=4, unit_type=lesson.unit_type_choices.NAZARI_AMALI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        self.test_lesson_obj_2.lesson_major.add(test_major)
        self.test_lesson_obj_2.pishniaz.set([test_lesson_obj_1])
        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        # ? creating professor
        test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")

        p_data = {
            "user":test_professor_user, 
            "first_name":"test", 
            "last_name":"test", 
            "date_of_birth":"1382-12-19",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test",
            "phone":"09121234567"
        }
        test_professor_obj = professor.objects.create(**p_data)

        # ? creating class for the lesson
        class_data_1 = {
            "lesson_code":test_lesson_obj_1,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"20:45:00",
            "class_end_time":"23:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4032,
        }
        self.test_class_obj_1 = lesson_class.objects.create(**class_data_1)

        class_data_2 = {
            "lesson_code":self.test_lesson_obj_2,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"17:45:00",
            "class_end_time":"19:45:00",
            "exam_date_time":"1405-03-12 12:00",
            "capacity":35,
            "class_code":301,
            "class_number":1212,
            "semester":4032,
        }
        self.test_class_obj_2 = lesson_class.objects.create(**class_data_2)
    
    def test_lesson_has_no_requirements(self):
        self.test_lesson_obj_2.pishniaz.set("")
        self.test_lesson_obj_2.save()

        self.assertTrue(check_lesson_requirements_status(self.test_class_obj_2, self.test_student_obj))



    def test_lesson_has_pishniaz_but_student_failed(self):
        assigned_class_data = {
            "student_name":self.test_student_obj,
            "chosen_class":self.test_class_obj_1,
            "semester":4031
        }
        student_choosing_lesson.objects.create(**assigned_class_data)

        assigend_grade_data = {
            "student_name":self.test_student_obj,
            "lesson_name":self.test_class_obj_1,
            "mark":9.75
        }
        Grade.objects.create(**assigend_grade_data)

        self.assertFalse(check_lesson_requirements_status(self.test_class_obj_2, self.test_student_obj))



    def test_lesson_has_pishniaz_and_student_passed(self):
        assigned_class_data = {
            "student_name":self.test_student_obj,
            "chosen_class":self.test_class_obj_1,
            "semester":4031
        }
        student_choosing_lesson.objects.create(**assigned_class_data)

        assigend_grade_data = {
            "student_name":self.test_student_obj,
            "lesson_name":self.test_class_obj_1,
            "mark":15
        }
        Grade.objects.create(**assigend_grade_data)

        self.assertTrue(check_lesson_requirements_status(self.test_class_obj_2, self.test_student_obj))