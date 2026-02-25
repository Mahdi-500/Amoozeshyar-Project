from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django_jalali.db.models import jdatetime
from academic.models import university, major, group
from LessonsApp.models import lesson
from StudentsApp.models import student_choosing_lesson
from ..models import *
from ..forms import *

class testProfessorForm(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username="testadmin", password="test")
        Group.objects.create(name="admin")
        self.admin.groups.add(Group.objects.get(name="admin"))
        self.client.login(username="testadmin", password="test")

        self.test_uni_1 = university.objects.create(name="test", code=500, address="test")
        self.test_uni_2 = university.objects.create(name="test2", code=501, address="test address")

        with open("academic/tests/test_photo.jpg", "rb") as f:
            self.photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")

    def test_help_texts(self):
        response = self.client.get(reverse("academic:register_professor"))
        self.assertContains(response, "مثال: 09121234567")
        self.assertContains(response, "مثال: 25-05-1357")



    def test_with_wrong_data(self):
        form_date = {
            "first_name": "مح4د ع@ی",
            "last_name":"حدا85د@",
            "date_of_birth":jdatetime.date(1382,10,12),
            "address":"این1 یک آدر# برای تست کر&ن است",
            "professor_id":"0f@23g45",
            "major":"مهند#سی کام1پیو%تر",
            "email":"testeamil.com",
            "phone":"+98811212345678",
            "universities":[self.test_uni_1.pk, self.test_uni_2.pk],
        }

        response = self.client.post(reverse("academic:register_professor"), data={**form_date, "photo":self.photo})
        form = response.context["form"]
        self.assertFormError(form, errors="فقط حروف الفبا در نام و نام خانوادگی مجاز است", field="first_name")
        self.assertFormError(form, errors="فقط حروف الفبا در نام و نام خانوادگی مجاز است", field="last_name")
        self.assertFormError(form, errors="فقط حروف الفبا مجاز است", field="address")
        self.assertFormError(form, errors=["شماره موبایل نامعتبر است", "شماره موبایل باید شامل 11 عدد باشد"], field="phone")
        self.assertFormError(form, errors="فقط حروف الفبا مجاز است", field="major")
        self.assertFormError(form, errors=["فقط عدد مجاز است", "کد ملی باید 10 کاراکتر باشد"], field="professor_id")
        self.assertFalse(professor.objects.filter(professor_id="0f@23g45").exists())


        
    def test_duplicate_id(self):
        test_major = major.objects.create(name="test", code=300, capacity=2000)
        student.objects.create(user= self.admin, first_name="test", last_name="test", date_of_birth=jdatetime.date(1382,10,12),
                            student_id="0123456789", photo=self.photo, university=self.test_uni_1, major=test_major)
        form_date = {
            "first_name": "مح4د ع@ی",
            "last_name":"حدا85د@",
            "date_of_birth":jdatetime.date(1382,10,12),
            "address":"این1 یک آدر# برای تست کر&ن است",
            "professor_id":"0123456789",
            "major":"مهند#سی کام1پیو%تر",
            "email":"testeamil.com",
            "phone":"+98811212345678",
            "universities":[self.test_uni_1.pk, self.test_uni_2.pk],
        }
        response = self.client.post(reverse("academic:register_professor"), data={**form_date, "photo":self.photo})
        form = response.context["form"]
        self.assertFormError(form, errors="کد ملی را با دقت وارد کنید", field="professor_id")
    


    def test_with_correct_data(self):
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        form_date = {
            "first_name": "محمد علی",
            "last_name":"حدادی",
            "date_of_birth":jdatetime.date(1382,10,12),
            "address":"این یک آدرس برای تست کردن است",
            "professor_id":"1234567890",
            "major":"مهندسی کامپیوتر",
            "email":"testeamil@gmail.com",
            "phone":"+989121234567",
            "universities":[self.test_uni_1.pk, self.test_uni_2.pk],
        }
        response = self.client.post(reverse("academic:register_professor"), data={**form_date, "photo":photo}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("academic:main"))
        self.assertTrue("ثبت نام موفقیت آمیز بود" == str(messages[0]))
        self.assertTrue(professor.objects.filter(professor_id="1234567890").exists())



class testGradeForm(TestCase):
    def setUp(self):
        # ? creating professor user
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
        self.client.login(username="testuser", password="test")

        # ? creating university
        self.test_uni = university.objects.create(name="test", code=500, address="test")
        
        # ? creating major
        self.test_major = major.objects.create(name="test", code=100, capacity=1000)

        # ? creating students
        test_student_1 = User.objects.create_user(username="teststudent1", password="test")
        test_student_2 = User.objects.create_user(username="teststudent2", password="test")
        test_student_3 = User.objects.create_user(username="teststudent3", password="test")


        self.test_student_1 = student.objects.create(user=test_student_1, first_name = "test", last_name="test", date_of_birth=jdatetime.date(1382,10,10), student_id="0123456789",
                            photo=photo, marriage=False, mobile="09121234567", address="test", gender=student.gender_choices.MALE, 
                            major=self.test_major, university=self.test_uni, status=student.status_choices.STUDYING)
        
        self.test_student_2 = student.objects.create(user=test_student_2, first_name = "test", last_name="test", date_of_birth=jdatetime.date(1380,10,10), student_id="1234567890",
                            photo=photo, marriage=True, mobile="09121234567", address="test", gender=student.gender_choices.FEMALE, 
                            major=self.test_major, university=self.test_uni, status=student.status_choices.STUDYING)
        
        self.test_student_3 = student.objects.create(user=test_student_3, first_name = "test", last_name="test", date_of_birth=jdatetime.date(1379,12,10), student_id="1123456789",
                            photo=photo, marriage=True, mobile="09121234567", address="test", gender=student.gender_choices.MALE, 
                            major=self.test_major, university=self.test_uni, status=student.status_choices.STUDYING)
        
        # ? creating lesson
        self.test_lesson = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)

        self.test_lesson.lesson_major.add(self.test_major)

        # ? creating lesson group
        self.test_group = group.objects.create(name="test", code=500)

        # ? creating lesson class
        data = {
            "lesson_code":self.test_lesson,
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
        self.test_class = lesson_class.objects.create(**data)

        # ? assigning students to the class
        student_choosing_lesson.objects.create(student_name=self.test_student_1, chosen_class=self.test_class, semester=4032)
        student_choosing_lesson.objects.create(student_name=self.test_student_2, chosen_class=self.test_class, semester=4032)
        student_choosing_lesson.objects.create(student_name=self.test_student_3, chosen_class=self.test_class, semester=4032)



    def test_with_wrong_data(self):
        form_data = {
            "form-TOTAL_FORMS": '3',
            "form-INITIAL_FORMS": '1',
            "form-0-first_name":self.test_student_1.first_name,
            "form-0-last_name":self.test_student_1.last_name,
            "form-0-student_number":self.test_student_1.student_number,
            "form-0-score":22,
            "form-1-first_name":self.test_student_2.first_name,
            "form-1-last_name":self.test_student_2.last_name,
            "form-1-student_number":self.test_student_2.student_number,
            "form-1-score":-1,
            "form-2-first_name":self.test_student_3.first_name,
            "form-2-last_name":self.test_student_3.last_name,
            "form-2-student_number":self.test_student_3.student_number,
            "form-2-score":12.658
        }

        session = self.client.session
        session["p_code"] = self.test_professor.code
        session.save()
        response = self.client.post(reverse("academic:grade", kwargs={"l_code":self.test_lesson.code, "class_code":self.test_class.class_code}), data={**form_data})
        formset = response.context["formset"]
        self.assertFormSetError(formset=formset, form_index=0, errors="نمره باید بین 0 تا 20 باشد", field="score")
        self.assertFormSetError(formset=formset, form_index=1, errors="نمره باید بین 0 تا 20 باشد", field="score")
        self.assertFormSetError(formset=formset, form_index=2, errors="فرمت نمره صحیح نیست", field="score")
        self.assertFalse(Grade.objects.filter(student_name=self.test_student_1, lesson_name=self.test_class).exists())
        self.assertFalse(Grade.objects.filter(student_name=self.test_student_2, lesson_name=self.test_class).exists())
        self.assertFalse(Grade.objects.filter(student_name=self.test_student_3, lesson_name=self.test_class).exists())



    def test_with_correct_data(self):
        form_data = {
            "form-TOTAL_FORMS": '3',
            "form-INITIAL_FORMS": '1',
            "form-0-first_name":self.test_student_1.first_name,
            "form-0-last_name":self.test_student_1.last_name,
            "form-0-student_number":self.test_student_1.student_number,
            "form-0-score":20,
            "form-1-first_name":self.test_student_2.first_name,
            "form-1-last_name":self.test_student_2.last_name,
            "form-1-student_number":self.test_student_2.student_number,
            "form-1-score":17.25,
            "form-2-first_name":self.test_student_3.first_name,
            "form-2-last_name":self.test_student_3.last_name,
            "form-2-student_number":self.test_student_3.student_number,
            "form-2-score":12.75
        }

        session = self.client.session
        session["p_code"] = self.test_professor.code
        session.save()
        response = self.client.post(reverse("academic:grade", kwargs={"l_code":self.test_lesson.code, "class_code":self.test_class.class_code}), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("academic:main"))
        self.assertTrue("ثبت نمره با موفقیت انجام شد" == str(messages[0]))
        self.assertTrue(Grade.objects.filter(student_name=self.test_student_1, lesson_name=self.test_class).exists())
        self.assertTrue(Grade.objects.filter(student_name=self.test_student_2, lesson_name=self.test_class).exists())
        self.assertTrue(Grade.objects.filter(student_name=self.test_student_3, lesson_name=self.test_class).exists())