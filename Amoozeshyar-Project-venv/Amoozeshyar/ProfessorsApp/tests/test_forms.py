from django.test import TestCase
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
        # ? creating users
        self.test_professor_user = User.objects.create_user(username="test_professor", password="test_pass")
        Group.objects.create(name="professor")
        self.test_professor_user.groups.add(Group.objects.get(name="professor"))

        self.test_uni_1 = university.objects.create(name="test", code=500, address="test")
        self.test_uni_2 = university.objects.create(name="test2", code=501, address="test address")

        with open("ProfessorsApp/tests/test_photo.jpg", "rb") as f:
            self.photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")

    def test_help_texts(self):
        form = ProfessorForm()
        self.assertEqual(form.fields['phone'].help_text, "مثال: 09121234567")
        self.assertEqual(form.fields['date_of_birth'].help_text, "مثال: 25-05-1357")



    def test_invalid_date_of_birth(self):
        # ? invalid month
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-13-12",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"09121234567",
            "universities":self.test_uni_1.pk
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["date_of_birth"], ["تاریخ نامعتبر است"])

        # ? invalid day
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-35",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"09121234567",
            "universities":self.test_uni_1.pk
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["date_of_birth"], ["تاریخ نامعتبر است"])

    

    def test_invalid_email(self):
        # ? without @
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"testgmail.com",
            "phone":"09121234567",
            "universities":self.test_uni_1.pk
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["ایمیل نامعتبر است"])

        # ? without .com
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail",
            "phone":"09121234567",
            "universities":self.test_uni_1.pk
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["ایمیل نامعتبر است"])

        # ? without the gmail part
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@.com",
            "phone":"09121234567",
            "universities":self.test_uni_1.pk
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["ایمیل نامعتبر است"])



    def test_invalid_phone_number(self):
        # ? more than 11 characters
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"091212345678",
            "universities":self.test_uni_1.pk
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["phone"], ["شماره موبایل نامعتبر است", "شماره موبایل باید شامل 11 رقم باشد"])

        # ? less than 11 characters
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"0912123456",
            "universities":self.test_uni_1.pk
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["phone"], ["شماره موبایل نامعتبر است", "شماره موبایل باید شامل 11 رقم باشد"])

        # ? without the country code
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
            "universities":self.test_uni_1.pk
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["phone"], ["شماره موبایل نامعتبر است"])



    def test_invalid_universities_field(self):
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["universities"], ["این فیلد اجباری است"])



    def test_invalid_first_name(self):
        form_data = {
            "user":self.test_professor_user,
            "first_name":"t@est",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["first_name"], ["فقط حروف الفبا در نام و نام خانوادگی مجاز است"])



    def test_invalid_last_name(self):
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"te/st",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["last_name"], ["فقط حروف الفبا در نام و نام خانوادگی مجاز است"])



    def test_invalid_address(self):
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test addr@/ess",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["address"], ["فقط حروف الفبا مجاز است"])



    def test_invalid_major(self):
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test maj0r",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["major"], ["فقط حروف الفبا مجاز است"])



    def test_invalid_professor_id(self):
        # ? none-int in id
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123!45678",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["professor_id"], ["فقط عدد مجاز است"])

        # ? more than 10 characters in id
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"01234567899",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["professor_id"], ["کد ملی باید 10 رقم باشد"])
        
        # ? less than 10 characters in id
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"01245678",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["professor_id"], ["کد ملی باید 10 رقم باشد"])



    def test_duplicate_id_in_another_table(self):
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

        student.objects.create(**form_data)

        prof_form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"00121234567",
        }
        form = ProfessorForm(data={**prof_form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["professor_id"], ["کد ملی را با دقت وارد کنید"])



    def test_with_correct_data(self):
        form_data = {
            "user":self.test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-10-20",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":self.photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"09121234567",
            "universities":[self.test_uni_1.pk]
        }
        media = {
            "photo":self.photo
        }
        form = ProfessorForm(data={**form_data}, files=media)
        self.assertTrue(form.is_valid())



class testGradeForm(TestCase):
    def test_labels(self):
        form = GradeForm()
        self.assertEqual(form["first_name"].label, "نام")
        self.assertEqual(form["last_name"].label, "نام خانوادگی")
        self.assertEqual(form["student_number"].label, "شماره دانشجویی")
        self.assertEqual(form["mark"].label, "نمره")



    def test_mark_errors(self):
        # ? max value
        form_data = {
            "mark":21
        }
        form = GradeForm(data={**form_data})
        self.assertIn("نمره باید بین 0 تا 20 باشد", form.errors["mark"])

        # ? min value
        form_data = {
            "mark":-1
        }
        form = GradeForm(data={**form_data})
        self.assertIn("نمره باید بین 0 تا 20 باشد", form.errors["mark"])

        # ? max decimal places
        form_data = {
            "mark":15.234
        }
        form = GradeForm(data={**form_data})
        self.assertIn("فرمت نمره صحیح نیست", form.errors["mark"])

    
    def test_readonly_attr(self):
        form = GradeForm()
        for i in ["first_name", "last_name", "student_number"]:
            self.assertTrue(form[i].field.widget.attrs["readonly"])



    def test_with_correct_data(self):
        # ? creating professor user
        with open("ProfessorsApp/tests/test_photo.jpg", "rb") as f:
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

        self.test_student_1 = student.objects.create(user=test_student_1, first_name = "test", last_name="test", date_of_birth=jdatetime.date(1382,10,10), student_id="0123456789",
                            photo=photo, marriage=False, mobile="09121234567", address="test", gender=student.gender_choices.MALE, 
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
            "exam_date_time":"1404-12-21 16:00",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
            "semester":4032,
        }
        self.test_class = lesson_class.objects.create(**data)

        # ? assigning students to the class
        student_choosing_lesson.objects.create(student_name=self.test_student_1, chosen_class=self.test_class, semester=4032)
        form_data = {
            "first_name":self.test_student_1.first_name,
            "last_name":self.test_student_1.last_name,
            "student_number":self.test_student_1.student_number,
            "mark":20,
        }

        form = GradeForm(data={**form_data})
        self.assertTrue(form.is_valid())