from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from ..models import *
from ..forms import *
class testLoginForm(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="testadmin", password="test")
        Group.objects.create(name="admin")



    def test_with_wrong_username_password(self):
        # ? testing with wrong username and password
        form_data = {
            "username":"test",
            "password":"test1"
        }
        response = self.client.post(reverse("academic:login"), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertTrue("نام کاربری یا رمز عبور صحیح نیست" == str(messages[0]))
        self.assertRedirects(response, reverse("academic:login"))



    def test_no_group(self):
        # ? testing with a user which doesn't have any group
        form_data = {
            "username":"testadmin",
            "password":"test"
        }
        response = self.client.post(reverse("academic:login"), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertTrue("گروهی برای شما تعیین نشده است" == str(messages[0]))
        self.assertRedirects(response, reverse("academic:login"))

    

    def test_with_correct_data(self):
        form_data = {
            "username":"testadmin",
            "password":"test"
        }
        self.admin.groups.add(Group.objects.get(name="admin"))
        response = self.client.post(reverse("academic:login"), data={**form_data}, follow=True)
        messages = list(response.context["messages"])
        self.assertTrue("وارد شدید" == str(messages[0]))
        self.assertRedirects(response, reverse("academic:main"))