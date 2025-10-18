from django import forms
from django.forms import formset_factory
from django_jalali.db import models as jmodels
from .models import student, professor, lesson, lesson_class, major

def semester() -> str: 
    today_date_month = jmodels.jdatetime.date.today().month
    today_date_year = str(jmodels.jdatetime.date.today().year)

    if 11 <= today_date_month <= 12:
        today_date_year[1:] + '2'
        
    elif 1 <= today_date_month <= 3:
        year = str(int(today_date_year) - 1)[1:]
        today_date_year = year + "2"

    elif 6 <= today_date_month <= 10:
        today_date_year[1:] + '1'

    elif today_date_month == 4 or today_date_month == 5:
        year = str(int(today_date_year) - 1)[1:]
        today_date_year = year + "3"

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
        }

    def clean(self):
        clean_data = super().clean()
        first_name = clean_data.get("first_name")
        last_name = clean_data.get("last_name")
        student_id = clean_data.get("student_id")
    
        space_fname = first_name.find(" ")
        space_lname = last_name.find(" ")

        # ? first name validation
        if space_fname != -1:
            first_name = first_name.split(' ')
            for i in first_name:
                if not i.isalpha():
                    self.add_error("first_name", "فقط حروف الفبا در نام و نام خانوادگی مجاز است")
        else:
            if not first_name.isalpha():
                self.add_error("first_name","فقط حروف الفبا در نام و نام خانوادگی مجاز است" )
            

        # ? last name validation
        if space_lname != -1:
            last_name = last_name.split(' ')
            for i in last_name:
                if not i.isalpha():
                    self.add_error("last_name","فقط حروف الفبا در نام و نام خانوادگی مجاز است")
        else:
            if not last_name.isalpha():
                self.add_error("last_name","فقط حروف الفبا در نام و نام خانوادگی مجاز است")
        
        if not student_id.isdigit():
            self.add_error("student_id", "فقط عدد مجاز است")
        
        if len(student_id) < 10:
            self.add_error("student_id", "کد ملی باید 10 کاراکتر باشد")
        

class ProfessorForm(forms.ModelForm):

    class Meta:
        model = professor
        fields = "__all__"
        exclude = ['created', 'modified', 'role', 'user', 'code']

        widgets = {
            "universities": forms.CheckboxSelectMultiple,
            "date_of_birth":forms.TextInput(attrs={
                "dir":"rtl"})
        }

        help_texts = {
            "phone":"مثال: 09121234567",
            "date_of_birth": "مثال: 25-12-1357",
        }

        error_messages = {
            "date_of_birth":{"invalid":"تاریخ نامعتبر است"},
        }

    def clean(self):
        clean_data = super().clean()
        first_name = clean_data.get("first_name")
        last_name = clean_data.get("last_name")
        major = clean_data.get("professor_major")
        professor_id = clean_data.get("professor_id")

        student_object = student.objects.all().filter(student_id=professor_id)

        if student_object:
            self.add_error("professor_id", "کد ملی را با دقت وارد کنید")
        
        if not first_name.isalpha() or not last_name.isalpha():
            self.add_error("first_name", "فقط حروف الفبا مجاز است")
        
        major = major.split(' ')
        for i in major:
            if not i.isalpha():
                self.add_error("professor_major", "فقط حروف الفبا مجاز است")
        
        if not professor_id.isdigit():
            self.add_error("professor_id", "فقط عدد مجاز است")
        
        if len(professor_id) < 10:
            self.add_error("professor_id", "کد ملی باید 10 کاراکتر باشد")
        

    # def save(self, commit=True):
    #     professor = super().save(commit=False)
    #     if commit:
    #         professor.save()
    #         # ? Save the many-to-many data
    #         self.save_m2m()
    #     return professor



class LessonForm(forms.ModelForm):
    class Meta:
        model = lesson
        fields = [
            "name", "unit", "unit_type", "lesson_type",
            "pishniaz", "hamniaz", "lesson_major"
        ]

        widgets = {
            "pishniaz": forms.CheckboxSelectMultiple,
            "hamniaz": forms.CheckboxSelectMultiple,
            "lesson_major":forms.CheckboxSelectMultiple
        }

    def clean(self):
        clean_data = super().clean()
        name = clean_data.get("name")
        # apply_to_all = clean_data.get("apply_to_all")

        for name in name.split(" "):
            if not name.isalpha() and not name.isalnum():
                self.add_error("name", " ترکیب عدد با حروف الفبا یا فقط حروف الفبا مجاز است")
            
        # if apply_to_all:
        #     clean_data["lesson_major"] = major.objects.none()

    #def save(self, commit)

class LessonClassFrom(forms.ModelForm):
    class Meta:
        model = lesson_class
        fields = "__all__"
        exclude = ['created', 'modified']

        help_texts = {
            "lesson_time":"مثال: 09:05 تا 15:00"
        }

        widgets = {
            "lesson_time":forms.TextInput(attrs={
                "dir":"rtl"
            })
        }

    def clean(self):
        clean_date = super().clean()
        time = clean_date.get("lesson_time")
        index = [i for i,x in enumerate(time) if x == ":"]
        temp = time.find("تا")

        # ? saving the numbers
        first_time_hour = time[:index[0]]
        first_time_minute = time[index[0] + 1:index[0] + 3]
        second_time_hour = time[index[1] - 2:index[1]]
        second_time_minute = time[index[1] + 1:]
        
        if len(index) != 2:
            raise forms.ValidationError("فرمت وارد شده صحیح نیست")
        
        if temp < 0:
            self.add_error("lesson_time", "کلمه ' تا ' حتما باید درج شود")
        
        if temp != 5 and temp != 6:
            self.add_error("lesson_time", "کلمه ' تا ' را براساس فرمت داده شده در جای مناسب قرار دهید")
        
        if not first_time_hour.isdigit() or not first_time_minute.isdigit() or not second_time_hour.isdigit() or not second_time_minute.isdigit():
            self.add_error("lesson_time", "فرمت وارد شده صحیح نیست")
        
        if (int(first_time_hour) > 24 or int(first_time_hour) < 1) or (int(second_time_hour) > 24 or int(second_time_hour) < 1):
            self.add_error("lesson_time", "مقدار ساعت باید بین 1 تا 24 باشد")
        
        if (int(first_time_minute) > 59 or int(first_time_minute) < 0) or (int(second_time_minute) > 59 or int(second_time_minute) < 0):
            self.add_error("lesson_time", "مقدار دقیقه باید بین 1 تا 59 باشید")
        


class GradeForm(forms.Form):

    first_name = forms.CharField(max_length=100, label="نام")
    last_name = forms.CharField(max_length=150, label="نام خانوادگی")
    student_id = forms.CharField(max_length=12, label="شماره دانشجویی")
    score = forms.DecimalField(label="نمره", required=True, decimal_places=2 ,widget=forms.NumberInput(attrs={"step":0.25, "min":0, "max":20}))
    
    def clean(self):
        clean_data = super().clean()
        first_name = clean_data.get("first_name")
        last_name = clean_data.get("last_name")
        student_id = clean_data.get("student_id")
        
        if not first_name.isalpha() or not last_name.isalpha():
            raise forms.ValidationError("فقط حروف الفبا مجاز است")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_f_name = self.fields['first_name']
        field_l_name = self.fields['last_name']
        field_student_id = self.fields["student_id"]

        field_f_name.widget.attrs['readonly'] = True
        field_l_name.widget.attrs["readonly"] = True
        field_student_id.widget.attrs["readonly"] = True
GradeFormset = formset_factory(GradeForm, extra=0)



class LoginForm(forms.Form):
    username = forms.CharField(label="نام کاربری", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور", required=True)



class LessonSearchForm(forms.Form):

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



class ChoosingLessonForm(forms.Form):
    today_date_year = semester()
        
    lesson_semester= forms.CharField(label="نیمسال", initial= today_date_year, required=False, widget=forms.HiddenInput())
    chosen_lesson = forms.ChoiceField(label="کلاس ها", widget=forms.RadioSelect, choices=[("default", "select")])

