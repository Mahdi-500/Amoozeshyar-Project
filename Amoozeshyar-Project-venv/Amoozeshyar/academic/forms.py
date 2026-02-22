from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="نام کاربری", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور", required=True)