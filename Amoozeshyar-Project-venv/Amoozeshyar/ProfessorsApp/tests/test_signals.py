from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, call
from academic.models import university
from ..models import professor

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