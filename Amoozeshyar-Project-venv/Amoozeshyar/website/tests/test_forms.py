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
            "major":self.test_major.pk,
            "university":self.test_uni_1.pk,
        }
        response = self.client.post(reverse("website:register_student"), data={**form_data, "photo":photo}, follow=True)
        messages = list(list(response.context["messages"]))
        self.assertRedirects(response, reverse("website:main"))
        for i in messages:
            self.assertTrue("ثبت نام موفقیت آمیز بود" == i.message)
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
            "address":"این یک آدرس برای تست کردن است",
            "professor_id":"1234567890",
            "major":"مهندسی کامپیوتر",
            "email":"testeamil@gmail.com",
            "phone":"+989121234567",
            "universities":[self.test_uni_1.pk, self.test_uni_2.pk],
        }
        response = self.client.post(reverse("website:register_professor"), data={**form_date, "photo":photo}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("website:main"))
        for i in messages:
            self.assertTrue("ثبت نام موفقیت آمیز بود" == i.message)
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
            "pishniaz":self.test_lesson_2.pk,
            "hamniaz":self.test_lesson_1.pk,
            "lesson_major":(self.test_major_1.pk, self.test_major_2.pk)
        }
        response = self.client.post(reverse("website:create_lesson"), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("website:main"))
        for i in messages:
            self.assertTrue("ثبت درس موفقیت آمیز بود" == i.message)
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
        self.assertContains(response, "مثال: 09:05")
        self.assertContains(response, "مثال: 13:25")



    def test_with_wrong_data(self):

        # ? testing with more than one or no ":" symbol
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"9:50:",
            "class_end_time":"1050",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors="باشد HH:MM زمان باید به فرمت", field="class_start_time")
        self.assertFormError(form, errors="باشد HH:MM زمان باید به فرمت", field="class_end_time")
        self.assertFalse(lesson_class.objects.filter(class_code=300, class_number=1212).exists())

        # ? testing with both start and end time being the same
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"23:45",
            "class_end_time":"23:45",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertTrue("ساعت شروع و پایان نمی توانند یکسان باشند" in form.non_field_errors())
        self.assertFalse(lesson_class.objects.filter(class_code=300, class_number=1212).exists())

        # ? testing with entered numbers being out of range
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"26:68",
            "class_end_time":"25:75",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertFormError(form, errors="باشد HH:MM زمان باید به فرمت", field="class_start_time")
        self.assertFormError(form, errors="باشد HH:MM زمان باید به فرمت", field="class_end_time")
        self.assertFalse(lesson_class.objects.filter(class_code=300, class_number=1212).exists())



    def test_with_correct_data(self):
        form_data = {
            "lesson_code":self.test_lesson.pk,
            "professor_name":self.test_professor.pk,
            "university_location":self.test_uni.pk,
            "group_name":self.test_group.pk,
            "class_start_time":"9:50",
            "class_end_time":"10:50",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4032,
        }
        response = self.client.post(reverse("website:lesson_class"), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("website:main"))
        for i in messages:
            self.assertTrue("کلاس با موفقیت ایجاد شد" == i.message)
        self.assertTrue(lesson_class.objects.filter(class_code=300, class_number=1212).exists())



class gradeFormTest(TestCase):
    def setUp(self):
        # ? creating professor user
        with open("website/tests/test_photo.jpg", "rb") as f:
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
        test_student_1 = User.objects.create(username="teststudent1", password="test")
        test_student_2 = User.objects.create(username="teststudent2", password="test")
        test_student_3 = User.objects.create(username="teststudent3", password="test")


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

        # ? creating group
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
        response = self.client.post(reverse("website:grade", kwargs={"l_code":self.test_lesson.code, "class_code":self.test_class.class_code}), data={**form_data})
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
        response = self.client.post(reverse("website:grade", kwargs={"l_code":self.test_lesson.code, "class_code":self.test_class.class_code}), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("website:main"))
        for i in messages:
            self.assertTrue("ثبت نمره با موفقیت انجام شد" == i.message)
        self.assertTrue(Grade.objects.filter(student_name=self.test_student_1, lesson_name=self.test_class).exists())
        self.assertTrue(Grade.objects.filter(student_name=self.test_student_2, lesson_name=self.test_class).exists())
        self.assertTrue(Grade.objects.filter(student_name=self.test_student_3, lesson_name=self.test_class).exists())