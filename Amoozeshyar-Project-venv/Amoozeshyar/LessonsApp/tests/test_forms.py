from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from ProfessorsApp.models import professor
from ..models import *
from ..forms import *
class testLessonForm(TestCase):
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

        response = self.client.post(reverse("academic:create_lesson"), data=form_data)
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
        response = self.client.post(reverse("academic:create_lesson"), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("academic:main"))
        self.assertTrue("ثبت درس موفقیت آمیز بود" == str(messages[0]))
        self.assertTrue(lesson.objects.filter(name="ریاضی مهندسی").exists())



class testLessonClassForm(TestCase):
    
    def setUp(self):
        with open("academic/tests/test_photo.jpg", "rb") as f:
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
        response = self.client.get(reverse("lesson:lesson_class"))
        self.assertContains(response, "مثال: 09:05")
        self.assertContains(response, "مثال: 13:25")



    # def test_for_time_symbol(self):

    #     # ? testing with more than one or no ":" symbol
    #     form_data = {
    #         "lesson_code":self.test_lesson,
    #         "professor_name":self.test_professor,
    #         "university_location":self.test_uni,
    #         "group_name":self.test_group,
    #         "class_start_time":"9:50:",
    #         "class_end_time":"1050",
    #         "capacity":35,
    #         "class_code":300,
    #         "class_number":1212,
    #     }
    #     response = self.client.post(reverse("academic:lesson_class"), data={**form_data})
    #     form = response.context["form"]
    #     self.assertFormError(form, errors="باشد HH:MM زمان باید به فرمت", field="class_start_time")
    #     self.assertFormError(form, errors="باشد HH:MM زمان باید به فرمت", field="class_end_time")
    #     self.assertFalse(lesson_class.objects.filter(class_code=300, class_number=1212).exists())



    def test_for_no_equal_times(self):
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
        response = self.client.post(reverse("lesson:lesson_class"), data={**form_data})
        form = response.context["form"]
        self.assertTrue("ساعت شروع و پایان نمی توانند یکسان باشند" in form.non_field_errors())
        self.assertFalse(lesson_class.objects.filter(class_code=300, class_number=1212).exists())



    # def test_time_out_of_range(self):
    #     # ? testing with entered numbers being out of range
    #     form_data = {
    #         "lesson_code":self.test_lesson,
    #         "professor_name":self.test_professor,
    #         "university_location":self.test_uni,
    #         "group_name":self.test_group,
    #         "class_start_time":"26:68",
    #         "class_end_time":"25:75",
    #         "capacity":35,
    #         "class_code":300,
    #         "class_number":1212,
    #     }
    #     response = self.client.post(reverse("academic:lesson_class"), data={**form_data})
    #     form = response.context["form"]
    #     self.assertFormError(form, errors="باشد HH:MM زمان باید به فرمت", field="class_start_time")
    #     self.assertFormError(form, errors="باشد HH:MM زمان باید به فرمت", field="class_end_time")
    #     self.assertFalse(lesson_class.objects.filter(class_code=300, class_number=1212).exists())



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
        response = self.client.post(reverse("lesson:lesson_class"), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertRedirects(response, reverse("academic:main"))
        self.assertTrue("کلاس با موفقیت ایجاد شد" == str(messages[0]))
        self.assertTrue(lesson_class.objects.filter(class_code=300, class_number=1212).exists())