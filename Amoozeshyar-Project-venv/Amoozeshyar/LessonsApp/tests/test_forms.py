from django.test import TestCase
from academic.models.major import major
from ..models import *
from ..forms import *

class testLessonForm(TestCase):
    def setUp(self):
        self.test_major = major.objects.create(name="test", code=300, capacity=300)



    def test_widgets(self):
        form_data = {
            "name":"test",
            "unit":3,
            "lesson_major":[self.test_major.pk]
        }
        form = LessonForm(data={**form_data})
        self.assertTrue(form.is_valid())

        from django import forms
        self.assertIsInstance(form.fields["pishniaz"].widget, forms.CheckboxSelectMultiple)
        self.assertIsInstance(form.fields["hamniaz"].widget, forms.CheckboxSelectMultiple)
        self.assertIsInstance(form.fields["lesson_major"].widget, forms.CheckboxSelectMultiple)



    def test_name_validation(self):
        # ? all numbers
        form_data = {
            "name":"123 456",
            "unit":3,
            "lesson_major":[self.test_major.pk]
        }
        form = LessonForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form["name"].errors, [" ترکیب عدد با حروف الفبا یا فقط حروف الفبا مجاز است"])

        # ? all symbols
        form_data = {
            "name":"@# %^",
            "unit":3,
            "lesson_major":[self.test_major.pk]
        }
        form = LessonForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form["name"].errors, [" ترکیب عدد با حروف الفبا یا فقط حروف الفبا مجاز است"])

        # ? mixed with symbols
        form_data = {
            "name":"te@st",
            "unit":3,
            "lesson_major":[self.test_major.pk]
        }
        form = LessonForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form["name"].errors, [" ترکیب عدد با حروف الفبا یا فقط حروف الفبا مجاز است"])

        form_data = {
            "name":"test tes$",
            "unit":3,
            "lesson_major":[self.test_major.pk]
        }
        form = LessonForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form["name"].errors, [" ترکیب عدد با حروف الفبا یا فقط حروف الفبا مجاز است"])



    def test_lesson_being_both_pishniaz_and_hamniaz(self):
        lesson_data = {
            "name":"test",
            "unit":2,
        }

        test_lesson = lesson.objects.create(**lesson_data)
        test_lesson.lesson_major.set([self.test_major])
        form_data = {
            "name":"test",
            "unit":3,
            "pishniaz":[test_lesson.pk],
            "hamniaz":[test_lesson.pk],
            "lesson_major":[self.test_major.pk]
        }
        form = LessonForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertEqual(form["pishniaz"].errors, ["یک درس نمی تواند هم پیش نیاز باشد و هم همنیاز"])




from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from ProfessorsApp.models import professor
class testLessonClassForm(TestCase):
    def setUp(self):
        # ? creating professor
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        self.test_professor_user = User.objects.create_user(username="test_professor", password="test")
        self.test_professor_obj = professor.objects.create(user=self.test_professor_user, first_name="test", last_name="test", date_of_birth="1382-12-19",
                                                    address="test", professor_id="0123456789", photo=photo,
                                                    major = "test", phone="09121234567")

        # ? creating major
        test_major = major.objects.create(name="test1", code=100, capacity=200)

        # ? creating lesson
        self.test_lesson = lesson.objects.create(name="test", code=200, unit=3)
        self.test_lesson.lesson_major.add(test_major)

        # ? creating university
        self.test_uni= university.objects.create(name="test", code=500, address="test")

        # ? creating group
        self.test_group = group.objects.create(name="test", code=500)


    def test_help_text_display(self):
        form = LessonClassFrom()
        self.assertEqual(form["class_start_time"].help_text, "AM/PM 09:05 :مثال")
        self.assertEqual(form["class_end_time"].help_text, "AM/PM 13:25 :مثال")
        self.assertEqual(form["exam_date_time"].help_text, "eg: 1404-06-09T15:05")



    def test_widgets(self):
        form = LessonClassFrom()
        self.assertIsInstance(form.fields["class_start_time"].widget, forms.TimeInput)
        self.assertIsInstance(form.fields["class_end_time"].widget, forms.TimeInput)
        self.assertIsInstance(form.fields["exam_date_time"].widget, forms.TextInput)
        self.assertEqual(form.fields["exam_date_time"].widget.attrs["placeholder"], 'YYYY-MM-DDTHH:MM')
        self.assertEqual(form.fields["exam_date_time"].widget.attrs["class"], 'datetime-input')
        self.assertIsInstance(form.fields["semester"].widget, forms.TextInput)
        self.assertTrue(form.fields["semester"].widget.attrs["readonly"])



    def test_class_time_validation(self):
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"13:00",
            "class_end_time":"13:00",
            "exam_date_time":"1405-10-01 11:00",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        form = LessonClassFrom(data={**form_data})

        self.assertFalse(form.is_valid())
        self.assertIn("ساعت شروع و پایان نمی توانند یکسان باشند", form.errors["__all__"])



    def test_exam_date_time_format(self):
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-10-01shgf11:00",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        form = LessonClassFrom(data={**form_data})

        self.assertFalse(form.is_valid())
        self.assertIn("باشد yyyy/mm/ddThh:mm تاریخ و زمان باید به فرمت", form["exam_date_time"].errors)



    def test_wrong_data_type_in_exam_date_time(self):
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"s@05-10-01T11:00",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        form = LessonClassFrom(data={**form_data})
        
        self.assertFalse(form.is_valid())
        self.assertIn("در تاریخ و ساعت فقط عدد مجاز است", form["exam_date_time"].errors)



    def test_no_T_in_exam_date_time(self):
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-10-01A11:00",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        form = LessonClassFrom(data={**form_data})

        self.assertFalse(form.is_valid())
        self.assertIn("حرف T وجود ندارد یا در مکان اشتباهی قرار داده شده", form["exam_date_time"].errors)



    def test_invalid_date_for_exam_date_time(self):
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1404-13-32T11:00",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        form = LessonClassFrom(data={**form_data})
        
        self.assertFalse(form.is_valid())
        self.assertEqual(["سال امتحان نمی تواند از سال فعلی کمتر باشد",
                        "ماه امتحان باید عددی بین 1 تا 12 باشد",
                        "روز امتحان باید عددی بین 1 تا 31 باشد"], form["exam_date_time"].errors)



    def test_invalid_time_for_exam_date_time(self):
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-12-12T06:60",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        form = LessonClassFrom(data={**form_data})
        
        self.assertFalse(form.is_valid())
        self.assertEqual(["ساعت امتحان باید عددی بین 7 تا 20 باشد",
                        "دقیقه امتحان باید عددی بین 0 تا 59 باشد"], form["exam_date_time"].errors)



    def test_with_correct_data(self):
        form_data = {
            "lesson_code":self.test_lesson,
            "professor_name":self.test_professor_obj,
            "university_location":self.test_uni,
            "group_name":self.test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-12-12T07:00",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        form = LessonClassFrom(data={**form_data})
        
        self.assertTrue(form.is_valid())