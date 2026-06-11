from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django_jalali.db.models import jdatetime
from academic.models import major, university, group
from LessonsApp.models import lesson, lesson_class
from ProfessorsApp.models import professor
from ..models import *
from ..forms import *

class testStudentForm(TestCase):
    def test_excluded_fields_not_showing(self):
        form = StudentForm()
        self.assertFalse(form.is_valid())
        excluded_fields = ["created", "modified", "role", "user", "last_year", "student_number"]
        for i in excluded_fields:
            self.assertNotIn(i, form.fields)
    


    def test_help_texts_showing(self):
        form = StudentForm()
        self.assertFalse(form.is_valid())
        self.assertEqual("مثال: 09121234567", form.fields["mobile"].help_text)
        self.assertEqual("مثال: 25-08-1357", form.fields["date_of_birth"].help_text)


    
    def test_invalid_date_of_birth(self):
        # ? invalid month
        form_data = {
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1406-13-01",
            "student_id":"0123456789",
            "mobile":"091212345678",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["date_of_birth"], "تاریخ نامعتبر است")

        # ? invalid day
        form_data = {
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1406-01-32",
            "student_id":"0123456789",
            "mobile":"091212345678",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["date_of_birth"], "تاریخ نامعتبر است")



    def test_duplicate_student_id(self):
        # ? create user
        test_student_user = User.objects.create_user(username="test_student", password="test_pass")

        # ? cretae university
        test_uni = university.objects.create(name="test", code=100)

        # ? creating major
        test_major = major.objects.create(name="test", code=200, capacity=200)

        # ? create student
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                        content=f.read(),
                                        content_type="image/jpeg")
        student_data = {
            "user":test_student_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1382-02-12",
            "student_id":"0123456789",
            "photo":photo,
            "mobile":"09121234567",
            "address":"test",
            "university":test_uni,
            "major":test_major
        }
        student.objects.create(**student_data)

        form_data = {
            "first_name":"test",
            "last_name":"test",
            "student_id":"0123456789",
            "mobile":"091212345678",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["student_id"], ["کد ملی را با دقت وارد کنید"])



    def test_letters_not_allowed_in_student_id(self):
        form_data = {
            "first_name":"test",
            "last_name":"test",
            "student_id":"0a12345678",
            "mobile":"091212345678",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["student_id"], ["فقط عدد مجاز است"])



    def test_not_enough_digits_for_student_id(self):
        form_data = {
            "first_name":"test",
            "last_name":"test",
            "student_id":"12345678",
            "mobile":"091212345678",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["student_id"], ["کد ملی باید 10 کاراکتر باشد"])



    def test_invalid_phone_number(self):
        form_data = {
            "first_name":"test",
            "last_name":"test",
            "student_id":"0123456789",
            "mobile":"091212345678",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["mobile"], ["شماره موبایل نامعتبر است"])



    def test_empty_phone_number(self):
        form_data = {
            "first_name":"test",
            "last_name":"test",
            "student_id":"0123456789",
            "mobile":"",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["mobile"], ["شماره موبایل باید شامل 11 عدد باشد"])
    



    def test_invalid_first_name(self):
        form_data = {
            "first_name":"test 54@jhsfd",
            "last_name":"test",
            "student_id":"0123456789",
            "mobile":"09121234567",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["first_name"], ["فقط حروف الفبا در نام و نام خانوادگی مجاز است"])



    def test_invalid_last_name(self):
        form_data = {
            "first_name":"test",
            "last_name":"test 54@jhsfd",
            "student_id":"0123456789",
            "mobile":"09121234567",
            "address":"test",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["last_name"], ["فقط حروف الفبا در نام و نام خانوادگی مجاز است"])



    def test_invalid_address(self):
        form_data = {
            "first_name":"test",
            "last_name":"test",
            "student_id":"0123456789",
            "mobile":"09121234567",
            "address":"te6564#st",
        }
        form = StudentForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors["address"], ["فقط حروف الفبا مجاز است"])



    def test_with_correct_data(self):
        # ? create user
        test_student_user = User.objects.create_user(username="test_student", password="test_pass")

        # ? cretae university
        test_uni = university.objects.create(name="test", code=100)

        # ? creating major
        test_major = major.objects.create(name="test", code=200, capacity=200)

        # ? create student
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        form_data = {
            "user":test_student_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1382-02-12",
            "student_id":"0123456789",
            "mobile":"09121234567",
            "photo":photo,
            "address":"test",
            "university":test_uni,
            "major":test_major
        }

        files_data = {
            "photo":photo,
        }
        form = StudentForm(data={**form_data}, files=files_data)
        self.assertTrue(form.is_valid())



class testLessonSearchForm(TestCase):
    def setUp(self):
        # ? creating lessons
        self.test_lesson_1 = lesson.objects.create(name="test1", unit=3, code="12345", unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        self.test_lesson_2 = lesson.objects.create(name="test2", unit=1, code="67890", unit_type=lesson.unit_type_choices.AMALI,
                                                lesson_type=lesson.lesson_type_choices.PAYE)
        
        # ? creating professors
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
            
        self.test_user = User.objects.create_user(username="testuser", password="test")
        Group.objects.create(name="professor")
        self.test_user.groups.add(Group.objects.get(name="professor"))

        self.test_professor = professor.objects.create(user=self.test_user, first_name="test", last_name="test", date_of_birth="1382-12-19",
                                                        address="test", professor_id="0123456789", photo=photo,
                                                        major = "test", phone="09121234567")
        
        # ? creating lesson group
        self.test_group = group.objects.create(name="test", code=500)

        # ? creating university
        self.test_uni = university.objects.create(name="test", code=500, address="test")

        # ? creating classes
        data = {
            "lesson_code":self.test_lesson_1,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"9:50",
            "class_end_time":"10:50",
            "exam_date_time":"1404-12-06 16:00",
            "exam_date_time":"1404-12-06 14:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4032,
        }
        lesson_class.objects.create(**data)

        data = {
            "lesson_code":self.test_lesson_2,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"17:15",
            "class_end_time":"14:50",
            "exam_date_time":"1404-12-06 14:00",
            "capacity":35,
            "class_code":302,
            "class_number":1201,
            "semester":4032,
        }
        lesson_class.objects.create(**data)
        
        # ? creating major
        self.test_major = major.objects.create(name="test", code=100, capacity=1000)

        # ? creating student
        self.test_student = User.objects.create_user(username="teststudent", password="test")
        Group.objects.create(name="student")
        self.test_student.groups.add(Group.objects.get(name="student"))
        student.objects.create(user=self.test_student, first_name = "test", last_name="test", date_of_birth=jdatetime.date(1382,10,10), student_id="0123456789",
                            photo=photo, marriage=False, mobile="09121234567", address="test", gender=student.gender_choices.MALE, 
                            major=self.test_major, university=self.test_uni, status=student.status_choices.STUDYING)
        self.client.login(username="teststudent", password="test")



    def test_form_errors(self):
        form_data = {
            "query_lesson_code":"01234",
            "query_lesson_name":"5445^&%@&"
        }
        response = self.client.post(reverse("student:lesson_search"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors="کد درس باید 10 کاراکتر باشد", field="query_lesson_code")
        self.assertFormError(form, errors="نام درس معتر نیست", field="query_lesson_name")



    def test_no_lesson_found(self):
        form_data = {
            "query_lesson_name":"something"
        }
        response = self.client.post(reverse("student:lesson_search"), data={**form_data})
        self.assertContains(response, "درسی پیدا نشد")