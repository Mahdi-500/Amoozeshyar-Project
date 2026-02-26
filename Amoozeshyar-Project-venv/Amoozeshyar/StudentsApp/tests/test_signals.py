from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, call
from academic.models import major, university
from ..models import student

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



    @patch("StudentsApp.models.log")
    def test_no_signal_on_user_update(self, mock):
        self.test_student.first_name="no test"
        self.test_student.save()
        mock.info.assert_has_calls([call(msg="set_student_number; this is an update"), call(msg="set_last_year; this is an update"), 
                                    call(msg="set_entrance_year; this is an update")], any_order=True)
        self.assertEqual(mock.info.call_count, 3)



    @patch("StudentsApp.models.log")
    def test_both_user_photo_delete(self, mock):
        self.test_student.delete()
        self.assertFalse(student.objects.filter(student_id="0123456789").exists())
        self.assertFalse(User.objects.filter(username="test").exists())
        mock.info.assert_has_calls([call(msg="student; photo deleted"), call(msg="student; user deleted")], any_order=True)
        self.assertEqual(mock.info.call_count, 2)