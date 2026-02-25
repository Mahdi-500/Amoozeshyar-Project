from django import forms
from django_jalali.db import models as jmodels
from .models import student

def semester() -> str: 
    today_date_month = jmodels.jdatetime.date.today().month
    today_date_year = str(jmodels.jdatetime.date.today().year)

    if today_date_month == 12 or today_date_month == 11:
        today_date_year = today_date_year[1:] + '2'
        
    elif 1 <= today_date_month <= 3:
        year = str(int(today_date_year) - 1)[1:]
        today_date_year = today_date_year = year + "2"

    elif 6 <= today_date_month <= 10:
        today_date_year = today_date_year[1:] + '1'

    elif today_date_month == 4 or today_date_month == 5:
        year = str(int(today_date_year) - 1)[1:]
        today_date_year = today_date_year = year + "3"

    return today_date_year


class StudentForm(forms.ModelForm):
    class Meta:
        model = student
        fields = "__all__"
        exclude = ["created", "modified", "role", "user", "last_year", "student_number"]

        help_texts = {
            "mobile": "مثال: 09121234567",
            "date_of_birth":"مثال: 25-08-1357",
        }

        widget = {
            "date_of_birth":forms.TextInput(attrs={
                "dir":"rtl"})
        }

        error_messages = {
            "date_of_birth":{"invalid":"تاریخ نامعتبر است"},
            "student_id":{"unique":"کد ملی را با دقت وارد کنید"},
            "mobile":{"invalid":"شماره موبایل نامعتبر است"}
        }

    def clean(self):
        clean_data = super().clean()
        first_name = clean_data.get("first_name")
        last_name = clean_data.get("last_name")
        student_id = clean_data.get("student_id")
        address = clean_data.get("address")
        phone_number = clean_data.get("mobile")
    
        no_space_first_name = first_name.replace(" ","")
        no_space_last_name = last_name.replace(" ","")
        no_space_address = address.replace(" ", "")

        # ? first name validation
        if not no_space_first_name.isalpha():
            self.add_error("first_name", "فقط حروف الفبا در نام و نام خانوادگی مجاز است")
            return clean_data
            

        # ? last name validation
        if not no_space_last_name.isalpha():
            self.add_error("last_name","فقط حروف الفبا در نام و نام خانوادگی مجاز است")
            return clean_data
        
        

        # ? studnet id validation
        if not student_id.isdigit():
            self.add_error("student_id", "فقط عدد مجاز است")
            return clean_data
        
        if len(student_id) != 10:
            self.add_error("student_id", "کد ملی باید 10 کاراکتر باشد")
            return clean_data

        
        # ? address validation
        if not no_space_address.isalpha():
            self.add_error("address", "فقط حروف الفبا مجاز است")
            return clean_data

        
        # ? mobile validation
        if not str(phone_number).startswith("+989"):
            self.add_error("mobile", "شماره موبایل معتبر نیست")
            return clean_data

        if phone_number is None:
                self.add_error("mobile","شماره موبایل باید شامل 11 عدد باشد")
                return clean_data



class StudentLessonSearchForm(forms.Form):

    LESSON_TYPE_CHOICES = [(None, "----------------"), 
                        ("اصلی", "اصلی"),
                        ("پایه", "پایه"),
                        ("عمومی", "عمومی"),
                        ("تخصصی", "تخصصی"),
                        ("اختیاری", "اختیاری")]

    UNIT_TYPE_CHOICES = [(None, "----------------"),
                        ("نظری", "نظری"),
                        ("نظری-عملی", "نظری - عملی"),
                        ("عملی", "عملی"),
                        ("آز", "آزمایشگاهی"),
                        ("کارآموزی", "کارآموزی")]
    
    today_date_year = semester()

    query_lesson_code = forms.IntegerField(label="کد درس", required=False)
    query_lesson_name = forms.CharField(label="نام درس", required=False, empty_value=None)
    query_lesson_semester= forms.CharField(label="نیمسال", initial= today_date_year, required=True)
    #query_lesson_location = forms.CharField(label="مکان برگذاری کلاس", required=False)
    query_unit_type = forms.TypedChoiceField(choices=UNIT_TYPE_CHOICES, label="نوع واحد", required=False, empty_value=None)
    query_lesson_type = forms.TypedChoiceField(choices=LESSON_TYPE_CHOICES, label="نوع درس", required=False, empty_value=None)

    def clean(self):
        clean_data = super().clean()
        lesson_code = clean_data.get("query_lesson_code")
        lesson_name = clean_data.get("query_lesson_name")

        if lesson_code is not None:
            if len(str(lesson_code)) != 10:
                self.add_error("query_lesson_code", "کد درس باید 10 کاراکتر باشد")
                return clean_data

            if not lesson_name.isalpha() or not lesson_name.isalnum():
                self.add_error("query_lesson_name", "نام درس معتر نیست")
                return clean_data



class ChoosingLessonForm(forms.Form):
    today_date_year = semester()
    #lesson_semester= forms.CharField(label="نیمسال", initial= today_date_year, required=False, widget=forms.TextInput(attrs={"readonly":"readonly"}))
    chosen_lesson = forms.ChoiceField(label="کلاس ها", widget=forms.RadioSelect, choices=[("default", "select")])