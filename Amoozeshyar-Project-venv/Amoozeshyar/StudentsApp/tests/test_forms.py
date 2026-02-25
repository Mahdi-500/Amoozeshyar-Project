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
    def setUp(self):
        admin = User.objects.create_user(username="testadmin", password="test")
        Group.objects.create(name="admin")
        admin.groups.add(Group.objects.get(name="admin"))
        self.client.login(username="testadmin", password="test")

        self.test_major = major.objects.create(name="test", code=100, capacity=1000)
        self.test_uni_1 = university.objects.create(name="test", code=500, address="test")

        with open("academic/tests/test_photo.jpg", "rb") as f:
            self.photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")

    def test_help_texts(self):
        response = self.client.get(reverse("academic:register_student"))
        self.assertContains(response, "مثال: 09121234567")
        self.assertContains(response, "مثال: 25-08-1357")
    


    def test_form_errors(self):
        form_data = {
            "first_name": "#@$565",
            "last_name":"#@565",
            "date_of_birth":jdatetime.date(1382,12,21),
            "student_id":"0f@23g45",
            "mobile":"+98811212345678",
            "address":"این1 یک آدر# برای تست کر&ن است",
            "major":self.test_major.pk,
            "university":self.test_uni_1.pk,
        }

        response = self.client.post(reverse("academic:register_student"), data={**form_data, "photo":self.photo})
        form = response.context["form"]
        self.assertFormError(form, errors="فقط حروف الفبا در نام و نام خانوادگی مجاز است", field="first_name")
        self.assertFormError(form, errors="فقط حروف الفبا در نام و نام خانوادگی مجاز است", field="last_name")
        self.assertFormError(form, errors=["فقط عدد مجاز است",  "کد ملی باید 10 کاراکتر باشد"], field="student_id")
        self.assertFormError(form, errors="فقط حروف الفبا مجاز است", field="address")
        self.assertFormError(form, errors=["شماره موبایل نامعتبر است", "شماره موبایل باید شامل 11 عدد باشد"], field="mobile")
        self.assertTemplateUsed(response, "register_student.html")
        self.assertFalse(student.objects.filter(**form_data).exists())



    def test_duplicate_id(self):
        test_student = User.objects.create_user(username="teststudents", password="test")
        student.objects.create(user=test_student, first_name = "test", last_name="test", date_of_birth=jdatetime.date(1382,10,10), student_id="0123456789",
                            photo=self.photo, marriage=False, mobile="09121234567", address="test", gender=student.gender_choices.MALE, 
                            major=self.test_major, university=self.test_uni_1, status=student.status_choices.STUDYING)
        form_data = {
            "first_name": "محم5د عل@",
            "last_name":"حدا85د@",
            "date_of_birth":jdatetime.date(1382,10,21),
            "student_id":"0123456789",
            "mobile":"+98811212345678",
            "address":"این1 یک آدر# برای تست کر&ن است",
            "major":self.test_major.pk,
            "university":self.test_uni_1.pk,
        }

        response = self.client.post(reverse("academic:register_student"), data={**form_data, "photo":self.photo})
        form = response.context["form"]
        self.assertFormError(form, errors="کد ملی را با دقت وارد کنید",field="student_id")
        self.assertFalse(student.objects.filter(**form_data).exists())
        self.assertTemplateUsed(response, "register_student.html")


    
    def test_with_correct_data(self):
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        form_data = {
            "first_name": "محمد",
            "last_name":"محمدی",
            "date_of_birth":jdatetime.date(1382,5,12),
            "student_id":"1234567890",
            "mobile":"+989121234567",
            "address":"این یک آدرس برای تست است",
            "major":self.test_major.pk,
            "university":self.test_uni_1.pk,
        }
        response = self.client.post(reverse("academic:register_student"), data={**form_data, "photo":photo}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("academic:main"))
        self.assertTrue("ثبت نام موفقیت آمیز بود" == str(messages[0]))
        self.assertTrue(student.objects.filter(**form_data).exists())



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
        response = self.client.post(reverse("academic:lesson_search"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors="کد درس باید 10 کاراکتر باشد", field="query_lesson_code")
        self.assertFormError(form, errors="نام درس معتر نیست", field="query_lesson_name")



    def test_no_lesson_found(self):
        form_data = {
            "query_lesson_name":"something"
        }
        response = self.client.post(reverse("academic:lesson_search"), data={**form_data})
        self.assertContains(response, "درسی پیدا نشد")