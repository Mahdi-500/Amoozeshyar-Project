from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, call
from ..models import student, professor, major, university, lesson, group, lesson_class

class testStudentSignals(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username="test", password="test")
        self.test_major = major.objects.create(name="test", code=100, capacity=300)
        self.test_uni = university.objects.create(name="test", code=200, address="test address")

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")
        self.data = {
            "user":self.test_user,
            "first_name":"test",
            "last_name":"testing",
            "date_of_birth":"1382-06-12",
            "student_id":"0123456789",
            "photo":photo,
            "marriage":False,
            "mobile":"09121234567",
            "address":"this is a test address",
            "major":self.test_major,
            "university":self.test_uni
        }
        self.test_student = student.objects.create(**self.data)



    def test_on_user_creation(self):
        self.assertTrue(hasattr(self.test_student, "last_year"))
        self.assertTrue(hasattr(self.test_student, "student_number"))
        self.assertNotEqual(self.test_student.student_number, "111111111111")
        self.assertNotEqual(self.test_student.last_year, "null")



    @patch("academic.models.log")
    def test_no_signal_on_user_update(self, mock):
        self.test_student.first_name="no test"
        self.test_student.save()
        mock.info.assert_has_calls([call(msg="set_student_number; this is an update"), call(msg="set_last_year; this is an update"), 
                                    call(msg="set_entrance_year; this is an update")], any_order=True)
        self.assertEqual(mock.info.call_count, 3)



    @patch("academic.models.log")
    def test_both_user_photo_delete(self, mock):
        self.test_student.delete()
        self.assertFalse(student.objects.filter(student_id="0123456789").exists())
        self.assertFalse(User.objects.filter(username="test").exists())
        mock.info.assert_has_calls([call(msg="student; photo deleted"), call(msg="student; user deleted")], any_order=True)
        self.assertEqual(mock.info.call_count, 2)




class testProfessorSingals(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username="test", password="test")
        self.test_uni = university.objects.create(name="test", code=200, address="test address")

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")
        self.data = {
            "user":self.test_user,
            "first_name":"test",
            "last_name":"testing",
            "date_of_birth":"1382-06-12",
            "address":"this is a test address",
            "marriage":False,
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test major",
            "phone":"09121234567",
        }
        self.test_professor = professor.objects.create(**self.data)
        self.test_professor.universities.add(self.test_uni)

    

    def test_on_user_creation(self):
        self.assertTrue(hasattr(self.test_professor, "code"))
        self.assertNotEqual(self.test_professor.code, "1111111111")



    @patch("academic.models.log")
    def test_no_signals_on_user_update(self, mock):
        self.test_professor.first_name = "no test"
        self.test_professor.save()
        mock.info.assert_called_once_with(msg="set_professor_code; this is an update")


    @patch("academic.models.log")
    def test_both_user_photo_delete(self, mock):
        self.test_professor.delete()
        self.assertFalse(professor.objects.filter(professor_id="0123456789").exists())
        self.assertFalse(User.objects.filter(username="test").exists())
        mock.info.assert_has_calls([call(msg="professor; photo deleted"), call(msg="professor; user deleted")], any_order=True)
        self.assertEqual(mock.info.call_count, 2)



class testLessonSignals(TestCase):
    def setUp(self):
        self.test_major = major.objects.create(name="test", code=100, capacity=300)
        self.data = {
            "name":"test lesson",
            "unit":3,
        }
        self.test_lesson = lesson.objects.create(**self.data)
        self.test_lesson.lesson_major.add(self.test_major)



    def test_on_lesson_creation(self):
        self.assertTrue(hasattr(self.test_lesson, "code"))
        self.assertNotEqual(self.test_lesson.code, "1111111111")
    


    @patch("academic.models.log")
    def test_no_signal_on_lesson_update(self, mock):
        self.test_lesson.name = "no test"
        self.test_lesson.save()
        mock.info.assert_called_once_with(msg="set_lesson_code; this is an update")



class testLesson_classSiganl(TestCase):
    def setUp(self):
        # ? creating university
        self.test_uni = university.objects.create(name="test", code=200, address="test address")
        
        # ? creating professor
        self.test_user = User.objects.create_user(username="test", password="test")

        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")

        self.professor_data = {
            "user":self.test_user,
            "first_name":"test",
            "last_name":"testing",
            "date_of_birth":"1382-06-12",
            "address":"this is a test address",
            "marriage":False,
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test major",
            "phone":"09121234567",
        }
        self.test_professor = professor.objects.create(**self.professor_data)
        self.test_professor.universities.add(self.test_uni)

        # ? creating group
        self.test_group = group.objects.create(name="test", code=500)

        # ? creating major
        self.test_major = major.objects.create(name="test", code=100, capacity=300)

        # ? creating lesson
        self.lesson_data = {
            "name":"test lesson",
            "unit":3,
        }
        self.test_lesson = lesson.objects.create(**self.lesson_data)
        self.test_lesson.lesson_major.add(self.test_major)

        # ? creating lesson_class
        self.lesson_class_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"9:50",
            "class_end_time":"11:50",
            "capacity":35,
            "class_code":300,
            "class_number":1212,
        }
        self.test_lesson_class = lesson_class.objects.create(**self.lesson_class_data)



    def test_on_lesson_class_creation(self):
        self.assertTrue(hasattr(self.test_lesson_class, "semester"))
        self.assertNotEqual(self.test_lesson_class.semester, "1111")
    


    @patch("academic.models.log")
    def test_no_signal_on_lesson_class_update(self, mock):
        self.test_lesson_class.class_number = 1210
        self.test_lesson_class.save()
        mock.info.assert_called_once_with(msg="set_semester; this is an update")
