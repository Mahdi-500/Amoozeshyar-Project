from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="نام کاربری", required=True, error_messages={"required":"این فیلد اجباری است"})
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور", required=True, error_messages={"required":"این فیلد اجباری است"})