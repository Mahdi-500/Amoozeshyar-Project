from django import forms
from django.forms import formset_factory
from .models import professor
from StudentsApp.models import student

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
            "phone":{"invalid":"شماره موبایل نامعتبر است"},
            "universities":{"required":"این فیلد اجباری است"}
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


class GradeForm(forms.Form):

    first_name = forms.CharField(max_length=100, label="نام")
    last_name = forms.CharField(max_length=150, label="نام خانوادگی")
    student_number = forms.CharField(max_length=12, label="شماره دانشجویی")
    score = forms.DecimalField(label="نمره", required=True, decimal_places=2 , min_value=0, max_value=20, 
                                error_messages={"max_value":"نمره باید بین 0 تا 20 باشد",
                                                "min_value":"نمره باید بین 0 تا 20 باشد",
                                                "max_decimal_places":"فرمت نمره صحیح نیست"},
                                widget=forms.NumberInput(attrs={"step":0.25, "min":0, "max":20}))
    
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_f_name = self.fields['first_name']
        field_l_name = self.fields['last_name']
        field_student_number = self.fields["student_number"]

        field_f_name.widget.attrs['readonly'] = True
        field_l_name.widget.attrs["readonly"] = True
        field_student_number.widget.attrs["readonly"] = True
GradeFormset = formset_factory(GradeForm, extra=0)