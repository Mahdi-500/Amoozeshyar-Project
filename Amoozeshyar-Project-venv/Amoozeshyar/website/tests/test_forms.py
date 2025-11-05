from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django_jalali.db.models import jdatetime
from ..models import *
from ..forms import *

class studentFormTest(TestCase):
    def setUp(self):
        admin = User.objects.create_user(username="testadmin", password="test")
        Group.objects.create(name="admin")
        admin.groups.add(Group.objects.get(name="admin"))
        self.client.login(username="testadmin", password="test")

        self.test_major = major.objects.create(name="test", code=100, capacity=1000)
        self.test_uni_1 = university.objects.create(name="test", code=500, address="test")


    def test_help_texts(self):
        response = self.client.get(reverse("website:register_student"))
        self.assertContains(response, "مثال: 09121234567")
        self.assertContains(response, "مثال: 25-08-1357")
    


    def test_form_with_wrong_data(self):
        with open("website/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
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

        response = self.client.post(reverse("website:register_student"), data={**form_data, "photo":photo})
        form = response.context["form"]
        self.assertFormError(form, errors="فقط حروف الفبا در نام و نام خانوادگی مجاز است", field="first_name")
        self.assertFormError(form, errors="فقط حروف الفبا در نام و نام خانوادگی مجاز است", field="last_name")
        self.assertFormError(form, errors=["فقط عدد مجاز است",  "کد ملی باید 10 کاراکتر باشد"], field="student_id")
        self.assertFormError(form, errors="فقط حروف الفبا مجاز است", field="address")
        self.assertFormError(form, errors=["شماره موبایل نامعتبر است", "شماره موبایل باید شامل 11 عدد باشد"], field="mobile")
        self.assertTemplateUsed(response, "register_student.html")
        self.assertFalse(student.objects.filter(**form_data).exists())


        # ? checking for another error in student id
        test_student = User.objects.create(username="teststudents", password="test")
        student.objects.create(user=test_student, first_name = "test", last_name="test", date_of_birth=jdatetime.date(1382,10,10), student_id="0123456789",
                            photo=photo, marriage=False, mobile="09121234567", address="test", gender=student.gender_choices.MALE, 
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

        response = self.client.post(reverse("website:register_student"), data={**form_data, "photo":photo})
        form = response.context["form"]
        self.assertFormError(form, errors="کد ملی را با دقت وارد کنید",field="student_id")
        self.assertFalse(student.objects.filter(**form_data).exists())
        self.assertTemplateUsed(response, "register_student.html")


    
    def test_form_with_correct_data(self):
        with open("website/tests/test_photo.jpg", "rb") as f:
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
            "gender":student.gender_choices.MALE,
            "major":self.test_major.pk,
            "university":self.test_uni_1.pk,
            "status":student.status_choices.STUDYING
        }
        response = self.client.post(reverse("website:register_student"), data={**form_data, "photo":photo})
        self.assertRedirects(response, reverse("website:main"))
        self.assertTrue(student.objects.filter(**form_data).exists())



class professorFormTest(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username="testadmin", password="test")
        Group.objects.create(name="admin")
        self.admin.groups.add(Group.objects.get(name="admin"))
        self.client.login(username="testadmin", password="test")

        self.test_uni_1 = university.objects.create(name="test", code=500, address="test")
        self.test_uni_2 = university.objects.create(name="test2", code=501, address="test address")


    def test_help_texts(self):
        response = self.client.get(reverse("website:register_professor"))
        self.assertContains(response, "مثال: 09121234567")
        self.assertContains(response, "مثال: 25-05-1357")



    def test_form_with_wrong_data(self):
        with open("website/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
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

        response = self.client.post(reverse("website:register_professor"), data={**form_date, "photo":photo})
        form = response.context["form"]
        self.assertFormError(form, errors="فقط حروف الفبا در نام و نام خانوادگی مجاز است", field="first_name")
        self.assertFormError(form, errors="فقط حروف الفبا در نام و نام خانوادگی مجاز است", field="last_name")
        self.assertFormError(form, errors="فقط حروف الفبا مجاز است", field="address")
        self.assertFormError(form, errors=["شماره موبایل نامعتبر است", "شماره موبایل باید شامل 11 عدد باشد"], field="phone")
        self.assertFormError(form, errors="فقط حروف الفبا مجاز است", field="major")
        self.assertFormError(form, errors=["فقط عدد مجاز است", "کد ملی باید 10 کاراکتر باشد"], field="professor_id")
        self.assertFalse(professor.objects.filter(professor_id="0f@23g45").exists())

        
        # ? testin for another error for professor id
        test_major = major.objects.create(name="test", code=300, capacity=2000)
        student.objects.create(user= self.admin, first_name="test", last_name="test", date_of_birth=jdatetime.date(1382,10,12),
                            student_id="0123456789", photo=photo, university=self.test_uni_1, major=test_major)
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
        response = self.client.post(reverse("website:register_professor"), data={**form_date, "photo":photo})
        form = response.context["form"]
        self.assertFormError(form, errors="کد ملی را با دقت وارد کنید", field="professor_id")
    


    def test_with_correct_data(self):
        with open("website/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        form_date = {
            "first_name": "محمد علی",
            "last_name":"حدادی",
            "date_of_birth":jdatetime.date(1382,10,12),
            "gender":professor.gender_choices.MALE,
            "address":"این یک آدرس برای تست کردن است",
            "professor_id":"1234567890",
            "major":"مهندسی کامپیوتر",
            "email":"testeamil@gmail.com",
            "phone":"+989121234567",
            "universities":[self.test_uni_1.pk, self.test_uni_2.pk],
        }
        response = self.client.post(reverse("website:register_professor"), data={**form_date, "photo":photo})
        self.assertRedirects(response, reverse("website:main"))
        self.assertTrue(professor.objects.filter(professor_id="1234567890").exists())



class lessonFormTests(TestCase):
    def setUp(self):
        admin = User.objects.create_user(username="testadmin", password="test")
        Group.objects.create(name="admin")
        admin.groups.add(Group.objects.get(name="admin"))
        self.client.login(username="testadmin", password="test")

        self.test_major_1 = major.objects.create(name="test1", code=100, capacity=200)
        self.test_major_2 = major.objects.create(name="test2", code=101, capacity=300)

        self.test_lesson_1 = lesson.objects.create(name="test1", unit=3, unit_type=lesson.unit_type_choices.NAZARI,
                                            lesson_type=lesson.lesson_type_choices.TAKHASOSI)
        self.test_lesson_2 = lesson.objects.create(name="test2", unit=4, unit_type=lesson.unit_type_choices.AMALI, 
                                            lesson_type=lesson.lesson_type_choices.PAYE)
        self.test_lesson_1.lesson_major.add(self.test_major_1, self.test_major_2)
        self.test_lesson_2.lesson_major.add(self.test_major_1, self.test_major_2)



    def test_with_wrong_data(self):
        form_data = {
            "name":"ریا@ی مهند!س 1",
            "unit":3,
            "unit_type":lesson.unit_type_choices.NAZARI,
            "lesson_type":lesson.lesson_type_choices.TAKHASOSI,
            "pishniaz":(self.test_lesson_1.pk, self.test_lesson_2.pk),
            "hamniaz":self.test_lesson_1.pk,
            "lesson_major":(self.test_major_1.pk, self.test_major_2.pk)
        }

        response = self.client.post(reverse("website:create_lesson"), data=form_data)
        form = response.context["form"]
        self.assertFormError(form, errors=" ترکیب عدد با حروف الفبا یا فقط حروف الفبا مجاز است", field="name")
        self.assertFormError(form, errors="یک درس نمی تواند هم پیش نیاز باشد و هم همنیاز", field="pishniaz")
        self.assertFalse(lesson.objects.filter(name="ریا@ی مهند!س 1").exists())

    

    def test_with_correct_data(self):
        form_data = {
            "name":"ریاضی مهندسی",
            "unit":3,
            "unit_type":lesson.unit_type_choices.NAZARI,
            "lesson_type":lesson.lesson_type_choices.TAKHASOSI,
            "pishniaz":self.test_lesson_2.pk,
            "hamniaz":self.test_lesson_1.pk,
            "lesson_major":(self.test_major_1.pk, self.test_major_2.pk)
        }
        response = self.client.post(reverse("website:create_lesson"), data={**form_data})
        self.assertRedirects(response, reverse("website:main"))
        self.assertTrue(lesson.objects.filter(name="ریاضی مهندسی").exists())



class lessonClassFormTests(TestCase):
    
    def setUp(self):
        with open("website/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
            
        self.admin = User.objects.create_user(username="testadmin", password="test")
        Group.objects.create(name="admin")
        self.admin.groups.add(Group.objects.get(name="admin"))
        self.client.login(username="testadmin", password="test")

        test_major = major.objects.create(name="test1", code=100, capacity=200)
        self.test_lesson = lesson.objects.create(name="test", code=200, unit=3)
        self.test_lesson.lesson_major.add(test_major)
        self.test_professor = professor.objects.create(user=self.admin, first_name="test", last_name="test", date_of_birth="1382-12-19",
                                                    address="test", professor_id="0123456789", photo=photo,
                                                    major = "test", phone="09121234567")
        self.test_uni= university.objects.create(name="test", code=500, address="test")
        self.test_group = group.objects.create(name="test", code=500)


    def test_help_text(self):
        response = self.client.get(reverse("website:lesson_class"))
        self.assertContains(response, "مثال: 09:05 تا 15:00")



    def test_with_wrong_data(self):

        # ? testing without the ":" symbol
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "lesson_time":"1050 تا 950",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors="فرمت وارد شده صحیح نیست", field="lesson_time")

        # ? testing without the word "تا"
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "lesson_time":"9:50 10:50",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors="کلمه ' تا ' حتما باید درج شود", field="lesson_time")

        # ? testing with the word "تا" in the wrong place
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "lesson_time":"تا 9:50 10:50",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors=["کلمه ' تا ' را براساس فرمت داده شده در جای مناسب قرار دهید", "فرمت وارد شده صحیح نیست"], field="lesson_time")

        # ? testing with numbers being replaced with words
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "lesson_time":"ساعتی تا ساعتی",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors="فرمت وارد شده صحیح نیست", field="lesson_time")

        # ? testing with wrong numbers
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "lesson_time":"25:65 jh 27:75",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors=["مقدار ساعت باید بین 1 تا 24 باشد", "مقدار دقیقه باید بین 1 تا 59 باشید", "کلمه ' تا ' را براساس فرمت داده شده در جای مناسب قرار دهید"], field="lesson_time")