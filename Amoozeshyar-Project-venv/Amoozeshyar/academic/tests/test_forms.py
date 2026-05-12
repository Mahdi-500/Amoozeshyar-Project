from django.test import TestCase
from django.urls import reverse
from ..forms import *
class testLoginForm(TestCase):
    def test_username_missing(self):
        form_data = {
            "username":"",
            "password":"test"
        }
        form = LoginForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertEqual(form.errors["username"], ["این فیلد اجباری است"])



    def test_password_missing(self):
        form_data = {
            "username":"test_user",
            "password":""
        }
        form = LoginForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertEqual(form.errors["password"], ["این فیلد اجباری است"])



    def test_both_fields_missing(self):
        form_data = {
            "username":"",
            "password":""
        }
        form = LoginForm(data={**form_data})
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertIn("username", form.errors)
        self.assertEqual(form.errors["password"], ["این فیلد اجباری است"])
        self.assertEqual(form.errors["username"], ["این فیلد اجباری است"])



    def test_labels(self):
        form_data = {
            "username":"test_user",
            "password":"test_pass"
        }
        form = LoginForm(data={**form_data})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.fields["username"].label, "نام کاربری")
        self.assertEqual(form.fields["password"].label, "رمز عبور")



    def test_widgets(self):
        form_data = {
            "username":"test_user",
            "password":"test_pass"
        }
        form = LoginForm(data={**form_data})
        self.assertTrue(form.is_valid())
        
        from django.forms import PasswordInput
        self.assertIsInstance(form.fields["password"].widget, PasswordInput)



    def test_attribute(self):
        form_data = {
            "username":"test_user",
            "password":"test_pass"
        }
        form = LoginForm(data={**form_data})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.fields["password"].required)
        self.assertTrue(form.fields["username"].required)


        
    def test_with_correct_data(self):
        form_data = {
            "username":"test_user",
            "password":"test_pass"
        }
        form = LoginForm(data={**form_data})
        self.assertTrue(form.is_valid())