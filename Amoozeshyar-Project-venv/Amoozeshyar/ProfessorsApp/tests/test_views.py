from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from academic.models import major, university, group
from LessonsApp.models import lesson, lesson_class
from ..models import professor

class testProfessorFormView(TestCase):

    def setUp(self):
        test_admin = User.objects.create_user(username="test_admin", password="test")

        Group.objects.create(name="admin")

        test_admin.groups.add(Group.objects.get(name="admin"))



    def test_when_user_is_not_logged_in(self):
        response = self.client.get(reverse("professor:register_professor"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/?next=/register-professor")
        self.assertTemplateUsed(response, "Login.html")



    def test_when_user_is_not_authorized(self):
        # ? creating professor
        test_professor = User.objects.create_user(username="test_professor", password="test")
        Group.objects.create(name="professor")
        test_professor.groups.add(Group.objects.get(name="professor"))

        self.client.login(username="test_professor", password="test")
        response = self.client.get(reverse("professor:register_professor"))
        self.assertTemplateUsed(response, "forbidden.html")



    def test_with_GET_method(self):
        self.client.login(username="test_admin", password="test")
        response = self.client.get(reverse("professor:register_professor"))
        self.assertTemplateUsed(response, "register_professor.html")
        self.assertIn("form", response.context)



    def test_with_POST_method(self):
        # ? creating university
        uni_object = university.objects.create(name="test", code=500, address="test")

        with open("ProfessorsApp/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")
        form_data = {
            "first_name":"test",
            "last_name":"testing",
            "date_of_birth":"160-10-21",
            "address":"test",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test major",
            "email":"testemail@gmail.com",
            "phone":"09121234567",
            "universities":(uni_object.pk)
        }

        self.client.login(username="test_admin", password="test")
        response = self.client.post(reverse("professor:register_professor"), data={**form_data}, format="multipart", follow=True)
        message = list(response.context["messages"])[0].message

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main.html")
        self.assertIn("ثبت نام موفقیت آمیز بود", message)
        self.assertTrue(professor.objects.filter(professor_id="0123456789").exists())



class testProfessorProfileView(TestCase):
    def test_when_user_is_not_logged_in(self):
        response = self.client.get(reverse("professor:professor_profile"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/?next=/professor/profile")
        self.assertTemplateUsed(response, "Login.html")



    def test_when_user_is_not_authorized(self):
        # ? creating user
        admin_user = User.objects.create_user(username="test_admin", password="test")
        admin_group = Group.objects.create(name="admin")
        admin_user.groups.add(admin_group)

        self.client.login(username="test_admin", password="test")
        response = self.client.get(reverse("professor:professor_profile"))
        self.assertTemplateUsed(response, "forbidden.html")



    def test_context_items(self):
        # ? creating user
        professor_user = User.objects.create_user(username="test_professor", password="test")
        professor_group = Group.objects.create(name="professor")
        professor_user.groups.add(professor_group)

        # ? creating professor
        with open("ProfessorsApp/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")

        test_uni_obj = university.objects.create(name="test", code=500, address="test")
        professor_data = {
            "user":professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-12-12",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"09121234567",
        }
        professor_obj = professor.objects.create(**professor_data)
        professor_obj.universities.set([test_uni_obj])

        self.client.login(username="test_professor", password="test")
        response = self.client.get(reverse("professor:professor_profile"))

        # ? context keys
        self.assertIn("professor", response.context.keys())
        self.assertIn("p_university", response.context.keys())

        # ? context values
        self.assertEqual(response.context["professor"], professor_obj)
        self.assertEqual(list(response.context["p_university"]), [test_uni_obj])

        self.assertTemplateUsed(response, "profile.html")



class testProfessorLessonListView(TestCase):
    def test_when_user_is_not_logged_in(self):
        response = self.client.get(reverse("professor:professor_lessons", kwargs={"p_code":"p_code", "u_code":"u_code"}), follow=True)
        self.assertRedirects(response, "/?next=/professor/classes/p_code/u_code")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Login.html")



    def test_when_user_is_not_authorized(self):
        test_admin = User.objects.create_user(username="test_admin", password="test")
        admin_group = Group.objects.create(name="admin")
        test_admin.groups.add(admin_group)

        self.client.login(username="test_admin", password="test")
        response = self.client.get(reverse("professor:professor_lessons", kwargs={"p_code":"p_code", "u_code":"u_code"}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "forbidden.html")



    def test_context_items(self):
        # ? creating user
        test_professor_user = User.objects.create_user(username="test_professor", password="test")
        professor_group = Group.objects.create(name="professor")
        test_professor_user.groups.add(professor_group)

        # ? creating professor
        with open("ProfessorsApp/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")

        test_uni = university.objects.create(name="test", code=500, address="test")
        professor_data = {
            "user":test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-12-12",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"09121234567",
        }
        test_professor_obj = professor.objects.create(**professor_data)
        test_professor_obj.universities.set([test_uni])

        # ? creating major
        test_major = major.objects.create(name="test", code=300, capacity=200)

        # ? creating lesson
        lesson_data = {
            "name":"test",
            "unit":3,
        }
        test_lesson = lesson.objects.create(**lesson_data)
        test_lesson.lesson_major.set([test_major])

        # ? creating group
        test_group = group.objects.create(name="test", code=200)

        # ? creating lesson class
        lesson_class_1_data = {
            "lesson_code":test_lesson,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-10-01 11:00",
            "capacity":35,
            "class_code":71,
            "class_number":1201
        }

        lesson_class_2_data = {
            "lesson_code":test_lesson,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"17:00",
            "class_end_time":"19:00",
            "exam_date_time":"1405-10-01 11:00",
            "capacity":35,
            "class_code":72,
            "class_number":1201
        }
        test_lesson_class_1 = lesson_class.objects.create(**lesson_class_1_data)
        lesson_class.objects.create(**lesson_class_2_data)

        self.client.login(username="test_professor", password="test")
        response = self.client.get(reverse("professor:professor_lessons", kwargs={"p_code":test_professor_obj.code, "u_code":test_uni.code}))

        # ? context keys
        self.assertIn("list", response.context.keys())
        self.assertIn("l_university", response.context.keys())

        # ? context values
        self.assertEqual(response.context["list"], [test_lesson_class_1])
        self.assertEqual(len(response.context["list"]), 1)
        self.assertEqual(response.context["l_university"], test_uni)
    


class testProfessorLessonDetailsView(TestCase):
    def test_when_user_is_not_logged_in(self):
        response = self.client.get(reverse("professor:professor_lesson_detail", kwargs={"l_code":"l_code"}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Login.html")
        self.assertRedirects(response, "/?next=/professor/lesson/details/l_code")



    def test_when_user_is_not_authorized(self):
        test_admin = User.objects.create_user(username="test_admin", password="test")
        admin_group = Group.objects.create(name="admin")
        test_admin.groups.add(admin_group)

        self.client.login(username="test_admin", password="test")
        response = self.client.get(reverse("professor:professor_lesson_detail", kwargs={"l_code":"l_code"}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "forbidden.html")



    def test_context_items(self):
        # ? creating user
        test_professor_user = User.objects.create_user(username="test_professor", password="test")
        professor_group = Group.objects.create(name="professor")
        test_professor_user.groups.add(professor_group)

        # ? creating professor
        with open("ProfessorsApp/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")

        test_uni = university.objects.create(name="test", code=500, address="test")
        professor_data = {
            "user":test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-12-12",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"09121234567",
        }
        test_professor_obj = professor.objects.create(**professor_data)
        test_professor_obj.universities.set([test_uni])

        # ? creating major
        test_major = major.objects.create(name="test", code=300, capacity=200)

        # ? creating lesson
        lesson_data = {
            "name":"test",
            "unit":3,
        }
        test_lesson = lesson.objects.create(**lesson_data)
        test_lesson.lesson_major.set([test_major])

        # ? creating group
        test_group = group.objects.create(name="test", code=200)

        # ? creating lesson class
        lesson_class_data = {
            "lesson_code":test_lesson,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-10-01 11:00",
            "capacity":35,
            "class_code":71,
            "class_number":1201
        }
        test_lesson_class = lesson_class.objects.create(**lesson_class_data)

        self.client.login(username="test_professor", password="test")
        session = self.client.session
        session["p_code"] = test_professor_obj.code
        session.save()
        response = self.client.get(reverse("professor:professor_lesson_detail", kwargs={"l_code":test_lesson.code}))

        # ? context keys
        self.assertIn("lesson", response.context.keys())
        self.assertIn("l_code", response.context.keys())

        # ? context values
        self.assertEqual(response.context["lesson"], [(test_lesson_class.class_day, test_lesson_class.class_code)])
        self.assertEqual(response.context["l_code"], test_lesson.code)



class testGradeFormView(TestCase):
    def test_when_user_is_not_logged_in(self):
        response = self.client.get(reverse("professor:grade", kwargs={"l_code":"l_code", "class_code":1234}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/?next=/professor/lesson/details/l_code/1234/submitting_grade")
        self.assertTemplateUsed(response, "Login.html")



    def test_when_user_is_not_authorized(self):
        test_admin = User.objects.create_user(username="test_admin", password="test")
        admin_group = Group.objects.create(name="admin")
        test_admin.groups.add(admin_group)

        response = self.client.get(reverse("professor:grade", kwargs={"l_code":"l_code", "class_code":1234}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "forbidden.html")



    def test_with_GET_method(self):
        # ? creating user
        test_professor_user = User.objects.create_user(username="test_professor", password="test")
        test_student_user_1 = User.objects.create_user(username="test_student_1", password="test")
        test_student_user_2 = User.objects.create_user(username="test_student_2", password="test")

        student_group = Group.objects.create(name="student")
        professor_group = Group.objects.create(name="professor")

        test_professor_user.groups.add(professor_group)
        test_student_user_1.groups.add(student_group)
        test_student_user_2.groups.add(student_group)
    
        # ? creating professor
        with open("ProfessorsApp/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")
    
        test_uni = university.objects.create(name="test", code=500, address="test")
        professor_data = {
            "user":test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-12-12",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"09121234567",
        }
        test_professor_obj = professor.objects.create(**professor_data)
        test_professor_obj.universities.set([test_uni])

        # ? creating major
        test_major = major.objects.create(name="test", code=300, capacity=200)

        # ? creating student
        student_info_1 = {
            "user":test_student_user_1,
            "first_name":"test",
            "last_name":"one",
            "date_of_birth":"1382-05-12",
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"09121234567",
            "major":test_major,
            "university":test_uni
        }

        student_info_2 = {
            "user":test_student_user_2,
            "first_name":"test",
            "last_name":"two",
            "date_of_birth":"1382-05-20",
            "student_id":"2345678901",
            "photo":photo,
            "mobile":"09121234567",
            "major":test_major,
            "university":test_uni
        }

        from StudentsApp.models import student
        test_student_obj_1 = student.objects.create(**student_info_1)
        test_student_obj_2 = student.objects.create(**student_info_2)

        # ? creating lesson
        lesson_data = {
            "name":"test",
            "unit":3,
        }
        test_lesson = lesson.objects.create(**lesson_data)
        test_lesson.lesson_major.set([test_major])
    
        # ? creating group
        test_group = group.objects.create(name="test", code=200)
    
        # ? creating lesson class
        lesson_class_data = {
            "lesson_code":test_lesson,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-10-01 11:00",
            "capacity":35,
            "class_code":71,
            "class_number":1201
        }
        test_lesson_class = lesson_class.objects.create(**lesson_class_data)

        # ? students choosing lesson
        from StudentsApp.models import student_choosing_lesson
        student_choosing_lesson.objects.create(student_name=test_student_obj_1, chosen_class=test_lesson_class)
        student_choosing_lesson.objects.create(student_name=test_student_obj_2, chosen_class=test_lesson_class)

        self.client.login(username="test_professor", password="test")
        session = self.client.session
        session["p_code"] = test_professor_obj.code
        session.save()
        response = self.client.get(reverse("professor:grade", kwargs={"l_code":test_lesson.code, "class_code":test_lesson_class.class_code}))

        # ? context key
        self.assertIn("formset", response.context.keys())

        # ? context values
        student_list = [test_student_obj_1, test_student_obj_2]
        form = response.context["formset"]
        for i, j in zip(range(0, 2), student_list):
            self.assertEqual(form[i]["first_name"].value(), j.first_name)
            self.assertEqual(form[i]["last_name"].value(), j.last_name)
            self.assertEqual(form[i]["student_number"].value(), j.student_number)
            self.assertEqual(form[i]["mark"].value(), 0)


    
    def test_with_POST_method(self):
        # ? creating user
        test_professor_user = User.objects.create_user(username="test_professor", password="test")
        test_student_user_1 = User.objects.create_user(username="test_student_1", password="test")
        test_student_user_2 = User.objects.create_user(username="test_student_2", password="test")
        
        student_group = Group.objects.create(name="student")
        professor_group = Group.objects.create(name="professor")
        
        test_professor_user.groups.add(professor_group)
        test_student_user_1.groups.add(student_group)
        test_student_user_2.groups.add(student_group)
        
        # ? creating professor
        with open("ProfessorsApp/tests/test_photo.jpg", "rb") as f:
            photo = SimpleUploadedFile(name="test_photo.jpg", content=f.read(), content_type="image/jpeg")
        
        test_uni = university.objects.create(name="test", code=500, address="test")
        professor_data = {
            "user":test_professor_user,
            "first_name":"test",
            "last_name":"test",
            "date_of_birth":"1360-12-12",
            "address":"test address",
            "professor_id":"0123456789",
            "photo":photo,
            "major":"test major",
            "email":"test@gmail.com",
            "phone":"09121234567",
        }
        test_professor_obj = professor.objects.create(**professor_data)
        test_professor_obj.universities.set([test_uni])
        
        # ? creating major
        test_major = major.objects.create(name="test", code=300, capacity=200)
        
        # ? creating student
        student_info_1 = {
            "user":test_student_user_1,
            "first_name":"test",
            "last_name":"one",
            "date_of_birth":"1382-05-12",
            "student_id":"1234567890",
            "photo":photo,
            "mobile":"09121234567",
            "major":test_major,
            "university":test_uni
        }
        
        student_info_2 = {
            "user":test_student_user_2,
            "first_name":"test",
            "last_name":"two",
            "date_of_birth":"1382-05-20",
            "student_id":"2345678901",
            "photo":photo,
            "mobile":"09121234567",
            "major":test_major,
            "university":test_uni
        }
        
        from StudentsApp.models import student
        test_student_obj_1 = student.objects.create(**student_info_1)
        test_student_obj_2 = student.objects.create(**student_info_2)
        
        # ? creating lesson
        lesson_data = {
            "name":"test",
            "unit":3,
        }
        test_lesson = lesson.objects.create(**lesson_data)
        test_lesson.lesson_major.set([test_major])
        
        # ? creating group
        test_group = group.objects.create(name="test", code=200)
        
        # ? creating lesson class
        lesson_class_data = {
            "lesson_code":test_lesson,
            "professor_name":test_professor_obj,
            "university_location":test_uni,
            "group_name":test_group,
            "class_start_time":"13:00",
            "class_end_time":"15:00",
            "exam_date_time":"1405-10-01 11:00",
            "capacity":35,
            "class_code":71,
            "class_number":1201
        }
        test_lesson_class = lesson_class.objects.create(**lesson_class_data)
        
        # ? students choosing lesson
        from StudentsApp.models import student_choosing_lesson
        student_choosing_lesson.objects.create(student_name=test_student_obj_1, chosen_class=test_lesson_class)
        student_choosing_lesson.objects.create(student_name=test_student_obj_2, chosen_class=test_lesson_class)
        
        self.client.login(username="test_professor", password="test")
        session = self.client.session
        session["p_code"] = test_professor_obj.code
        session.save()

        form_data = {
            "form-TOTAL_FORMS":2, 
            "form-INITIAL_FORMS":2,
            "form-0-first_name":test_student_obj_1.first_name,
            "form-0-last_name":test_student_obj_1.last_name,
            "form-0-student_number":test_student_obj_1.student_number,
            "form-0-mark":10,
            "form-1-first_name":test_student_obj_2.first_name,
            "form-1-last_name":test_student_obj_2.last_name,
            "form-1-student_number":test_student_obj_2.student_number,
            "form-1-mark":15
        }
        response = self.client.post(reverse("professor:grade", kwargs={"l_code":test_lesson.code, "class_code":test_lesson_class.class_code}), data={**form_data}, follow=True)
        message =list(response.context["messages"])[0].message

        from ProfessorsApp.models import Grade
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, "ثبت نمره با موفقیت انجام شد")
        self.assertTrue(Grade.objects.filter(student_name=test_student_obj_1.student_number).exists())
        self.assertTrue(Grade.objects.filter(student_name=test_student_obj_2.student_number).exists())