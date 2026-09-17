from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User, Group
from LessonsApp.models import lesson
from academic.models.major import major
from ..forms import LessonForm

class testLessonFormView(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="test_admin", password="test")
        Group.objects.create(name="admin")
        self.admin.groups.add(Group.objects.get(name="admin"))



    def test_when_user_is_not_logged_in(self):
        response = self.client.get(reverse("lesson:create_lesson"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/?next=/create_lesson")
        self.assertTemplateUsed(response, "Login.html")

        

    def test_when_user_is_not_authorized(self):
        # ? changing the group
        test_group = Group.objects.create(name="test")
        self.admin.groups.remove(Group.objects.get(name="admin"))
        self.admin.groups.add(test_group)

        self.client.login(username="test_admin", password="test")
        response = self.client.get(reverse("lesson:create_lesson"), follow=True)
        self.assertTemplateUsed(response, "forbidden.html")



    def test_with_GET_method(self):
        self.client.login(username="test_admin", password="test")
        response = self.client.get(reverse("lesson:create_lesson"))

        self.assertTemplateUsed(response, "register_lesson.html")
        self.assertIn("form", response.context.keys())
        self.assertIsInstance(response.context["form"], LessonForm)



    def test_with_POST_method(self):
        # ? creating major
        test_major = major.objects.create(name="test1", code=100, capacity=200)
        
        # ? creating lesson
        test_lesson = lesson.objects.create(name="test", unit=3)
        test_lesson.lesson_major.add(test_major)

        form_data = {
            "name":"test",
            "unit":2,
            "pishniaz":[test_lesson.pk],
            "lesson_major":[test_major.pk]
        }

        self.client.login(username="test_admin", password="test")
        response = self.client.post(reverse("lesson:create_lesson"), data={**form_data}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertRedirects(response, "/main/")
        self.assertEqual(message, "ثبت درس موفقیت آمیز بود")
        self.assertTrue(lesson.objects.filter(name="test", unit=2).exists())


from ..forms import LessonClassFrom
from ..models import lesson_class
class testLessonClassFormView(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="test_admin", password="test")
        Group.objects.create(name="admin")
        self.admin.groups.add(Group.objects.get(name="admin"))
    
    
    
    def test_when_user_is_not_logged_in(self):
        response = self.client.get(reverse("lesson:lesson_class"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/?next=/create_class")
        self.assertTemplateUsed(response, "Login.html")
    
    
    
    def test_when_user_is_not_authorized(self):
        # ? changing the group
        test_group = Group.objects.create(name="test")
        self.admin.groups.remove(Group.objects.get(name="admin"))
        self.admin.groups.add(test_group)
    
        self.client.login(username="test_admin", password="test")
        response = self.client.get(reverse("lesson:lesson_class"), follow=True)
        self.assertTemplateUsed(response, "forbidden.html")



    def test_with_GET_method(self):
        self.client.login(username="test_admin", password="test")

        response = self.client.get(reverse("lesson:lesson_class"))
        self.assertIn("form", response.context.keys())
        self.assertTemplateUsed(response, "add_lesson_class.html")
        self.assertIsInstance(response.context["form"], LessonClassFrom)



    def test_POST_method_with_overlap_error(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from ProfessorsApp.models import professor
        from academic.models import university, group
        # ? creating professor
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        test_professor_user = User.objects.create_user(username="test_professor", password="test")
        test_professor_obj = professor.objects.create(user=test_professor_user, first_name="test", last_name="test", date_of_birth="1382-12-19",
                                                    address="test", professor_id="0123456789", photo=photo,
                                                    major = "test", phone="09121234567")
        
        # ? creating major
        test_major = major.objects.create(name="test1", code=100, capacity=200)
        
        # ? creating lesson
        test_lesson = lesson.objects.create(name="test", code=200, unit=3)
        test_lesson.lesson_major.add(test_major)
        
        # ? creating university
        test_uni= university.objects.create(name="test", code=500, address="test")
        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        class_data_1 = {
            "lesson_code":test_lesson,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"13:00:00",
            "class_end_time":"15:00:00",
            "exam_date_time":"1405-12-12 07:00",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        temp_class = lesson_class.objects.create(**class_data_1)


        class_data_2 = {
            "lesson_code":test_lesson.pk,
            "professor_name":test_professor_obj.pk,
            "university_location":test_uni.pk,
            "group_name":test_group.pk,
            "class_day":"شنبه",
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-12-12T07:00",
            "capacity":35,
            "class_code":101,
            "class_number":1212
        }
        
        self.client.login(username="test_admin", password="test")
        response = self.client.post(reverse("lesson:lesson_class"), data={**class_data_2})
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, f"زمان و روز برگزاری این کلاس با  {temp_class}  تداخل دارد")
        self.assertTemplateUsed(response, "add_lesson_class.html")
        self.assertIn("form", response.context.keys())
        self.assertIsInstance(response.context["form"], LessonClassFrom)



    def test_POST_method_with_duplicate_class_code_error(self):
            from django.core.files.uploadedfile import SimpleUploadedFile
            from ProfessorsApp.models import professor
            from academic.models import university, group
            # ? creating professor
            with open("academic/tests/test_photo.jpg", "rb") as f:
                photo = SimpleUploadedFile(name="test_photo.jpg",
                                        content=f.read(),
                                        content_type="image/jpeg")
            test_professor_user = User.objects.create_user(username="test_professor", password="test")
            test_professor_obj = professor.objects.create(user=test_professor_user, first_name="test", last_name="test", date_of_birth="1382-12-19",
                                                        address="test", professor_id="0123456789", photo=photo,
                                                        major = "test", phone="09121234567")
            
            # ? creating major
            test_major = major.objects.create(name="test1", code=100, capacity=200)
            
            # ? creating lesson
            test_lesson = lesson.objects.create(name="test", code=200, unit=3)
            test_lesson.lesson_major.add(test_major)
            
            # ? creating university
            test_uni= university.objects.create(name="test", code=500, address="test")
            
            # ? creating group
            test_group = group.objects.create(name="test", code=500)
    
            class_data_1 = {
                "lesson_code":test_lesson,
                "professor_name":test_professor_obj,
                "university_location":test_uni,
                "group_name":test_group,
                "class_start_time":"13:00:00",
                "class_end_time":"15:00:00",
                "exam_date_time":"1405-12-13 07:00",
                "capacity":35,
                "class_code":100,
                "class_number":1212
            }
            lesson_class.objects.create(**class_data_1)
    
    
            class_data_2 = {
                "lesson_code":test_lesson.pk,
                "professor_name":test_professor_obj.pk,
                "university_location":test_uni.pk,
                "group_name":test_group.pk,
                "class_day":"یک شنبه",
                "class_start_time":"13:00",
                "class_end_time":"15:00",
                "exam_date_time":"1405-12-12T07:00",
                "capacity":35,
                "class_code":100,
                "class_number":1212
            }
            
            self.client.login(username="test_admin", password="test")
            response = self.client.post(reverse("lesson:lesson_class"), data={**class_data_2})
            message = list(response.context["messages"])[0].message
            self.assertEqual(message, "این کد ارائه در این نیمسال وجود دارد")
            self.assertTemplateUsed(response, "add_lesson_class.html")
            self.assertIn("form", response.context.keys())
            self.assertIsInstance(response.context["form"], LessonClassFrom)



    def test_with_correct_data(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from ProfessorsApp.models import professor
        from academic.models import university, group
        # ? creating professor
        with open("academic/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg",
                                    content=f.read(),
                                    content_type="image/jpeg")
        test_professor_user = User.objects.create_user(username="test_professor", password="test")
        test_professor_obj = professor.objects.create(user=test_professor_user, first_name="test", last_name="test", date_of_birth="1382-12-19",
                                                    address="test", professor_id="0123456789", photo=photo,
                                                    major = "test", phone="09121234567")
        
        # ? creating major
        test_major = major.objects.create(name="test1", code=100, capacity=200)
        
        # ? creating lesson
        test_lesson = lesson.objects.create(name="test", code=200, unit=3)
        test_lesson.lesson_major.add(test_major)
        
        # ? creating university
        test_uni= university.objects.create(name="test", code=500, address="test")
        
        # ? creating group
        test_group = group.objects.create(name="test", code=500)

        class_data = {
            "lesson_code":test_lesson.pk,
            "professor_name":test_professor_obj.pk,
            "university_location":test_uni.pk,
            "group_name":test_group.pk,
            "class_day":"یک شنبه",
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-12-12T07:00",
            "capacity":35,
            "class_code":100,
            "class_number":1212
        }
        
        self.client.login(username="test_admin", password="test")
        response = self.client.post(reverse("lesson:lesson_class"), data={**class_data}, follow=True)
        message = list(response.context["messages"])[0].message
        self.assertEqual(message, "کلاس با موفقیت ایجاد شد")