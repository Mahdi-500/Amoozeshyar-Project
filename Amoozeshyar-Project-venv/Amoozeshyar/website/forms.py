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
            

        # ? last name validation
        if not no_space_last_name.isalpha():
            self.add_error("last_name","فقط حروف الفبا در نام و نام خانوادگی مجاز است")
        
        

        # ? studnet id validation
        if not student_id.isdigit():
            self.add_error("student_id", "فقط عدد مجاز است")
        
        if len(student_id) != 10:
            self.add_error("student_id", "کد ملی باید 10 کاراکتر باشد")

        
        # ? address validation
        if not no_space_address.isalpha():
            self.add_error("address", "فقط حروف الفبا مجاز است")

        
        # ? mobile validation
        # if not str(phone_number).startswith("+989"):
        #     self.add_error("mobile", "شماره موبایل معتبر نیست")

        if phone_number is None:
                self.add_error("mobile","شماره موبایل باید شامل 11 عدد باشد")
        

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
            "date_of_birth": "مثال: 25-05-1357",
        }

        error_messages = {
            "date_of_birth":{"invalid":"تاریخ نامعتبر است"},
            "email":{"invalid":"ایمیل نامعبتر است"},
            "phone":{"invalid":"شماره موبایل نامعتبر است"}
        }

    def clean(self):
        clean_data = super().clean()
        first_name = clean_data.get("first_name")
        last_name = clean_data.get("last_name")
        address = clean_data.get("address")
        phone_number = clean_data.get("phone")
        major = clean_data.get("major")
        professor_id = clean_data.get("professor_id")

        no_space_first_name = first_name.replace(" ","")
        no_space_last_name = last_name.replace(" ","")
        no_space_address = address.replace(" ","")
        no_space_major = major.replace(" ","")

        student_object = student.objects.all().filter(student_id=professor_id)

        if student_object:
            self.add_error("professor_id", "کد ملی را با دقت وارد کنید")
        
        # ? first name validation
        if not no_space_first_name.isalpha():
            self.add_error("first_name", "فقط حروف الفبا در نام و نام خانوادگی مجاز است")
            

        # ? last name validation
        if not no_space_last_name.isalpha():
            self.add_error("last_name","فقط حروف الفبا در نام و نام خانوادگی مجاز است")
        

        # ? address validation
        if not no_space_address.isalpha():
            self.add_error("address", "فقط حروف الفبا مجاز است")


        # ? mobile validation
        # if not str(phone_number).startswith("+989"):
        #     self.add_error("phone", "شماره موبایل معتبر نیست")

        if phone_number is None:
                self.add_error("phone","شماره موبایل باید شامل 11 عدد باشد")


        # ? major validation
        if not no_space_major.isalpha():
            self.add_error("major", "فقط حروف الفبا مجاز است")
        

        # ? professor id validation
        if not professor_id.isdigit():
            self.add_error("professor_id", "فقط عدد مجاز است")
        
        if len(professor_id) != 10:
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
        pishniaz = clean_data.get("pishniaz")
        hamniaz = clean_data.get("hamniaz")

        no_space_name = name.replace(" ","")
        # apply_to_all = clean_data.get("apply_to_all")

        # ? lesson name validation
        for i in no_space_name:
            if not i.isalpha() and not i.isalnum():
                self.add_error("name", " ترکیب عدد با حروف الفبا یا فقط حروف الفبا مجاز است")
                break
        
        # ? pishniaz and hamniaz validation
        for i in pishniaz.all():
            for j in hamniaz.all():
                if i == j:
                    self.add_error("pishniaz", "یک درس نمی تواند هم پیش نیاز باشد و هم همنیاز")
        # if apply_to_all:
        #     clean_data["lesson_major"] = major.objects.none()

    #def save(self, commit)

class LessonClassFrom(forms.ModelForm):
    class Meta:
        model = lesson_class
        fields = "__all__"
        exclude = ['created', 'modified']

        help_texts = {
            "class_start_time":"مثال: 09:05",
            "class_end_time":"مثال: 13:25",
        }

        widgets = {
            "class_start_time":forms.TextInput(attrs={
                "dir":"rtl"
            }),
            "class_end_time":forms.TextInput(attrs={
                "dir":"rtl"
            })
        }

    def clean(self):
        clean_date = super().clean()
        start_time = clean_date.get("class_start_time")
        end_time = clean_date.get("class_end_time")
        start_index = [i for i,x in enumerate(start_time) if x == ":"]
        end_index = [i for i,x in enumerate(end_time) if x == ":"]

        if len(start_index) != 1:
            self.add_error("class_start_time", "فقط یک ':' مجاز است")
            return
        
        if len(end_index) != 1:
            self.add_error("class_end_time", "فقط یک ':' مجاز است")
            return
        
        start_time = start_time.replace(":", "")
        end_time = end_time.replace(":","")
        
        if start_time == end_time:
            raise forms.ValidationError("ساعت شروع و پایان نمی توانند یکسان باشند")
        
        if len(start_time) != 4:
            self.add_error("class_start_time", "عدد ها را مانند مثال های داده شده وارد کنید")

        elif not 0 < int(start_time) < 2359:
            self.add_error("class_start_time","ساعت باید عددی بین 1 تا 23 و دقیقه باید عددی بین 0 تا 59 باشد")
        
        if len(end_time) != 4:
            self.add_error("class_end_time", "عدد ها را مانند مثال های داده شده وارد کنید")
        
        elif not 0 < int(end_time) < 2359:
            self.add_error("class_end_time","ساعت باید عددی بین 1 تا 23 و دقیقه باید عددی بین 0 تا 59 باشد")
        


class GradeForm(forms.Form):

    first_name = forms.CharField(max_length=100, label="نام")
    last_name = forms.CharField(max_length=150, label="نام خانوادگی")
    student_number = forms.CharField(max_length=12, label="شماره دانشجویی")
    score = forms.DecimalField(label="نمره", required=True, decimal_places=2 ,widget=forms.NumberInput(attrs={"step":0.25, "min":0, "max":20}))
    
    def clean(self):
        clean_data = super().clean()
        first_name = clean_data.get("first_name")
        last_name = clean_data.get("last_name")
        student_number = clean_data.get("student_number")
        
        if not first_name.isalpha() or not last_name.isalpha():
            raise forms.ValidationError("فقط حروف الفبا مجاز است")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_f_name = self.fields['first_name']
        field_l_name = self.fields['last_name']
        field_student_number = self.fields["student_number"]

        field_f_name.widget.attrs['readonly'] = True
        field_l_name.widget.attrs["readonly"] = True
        field_student_number.widget.attrs["readonly"] = True
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

