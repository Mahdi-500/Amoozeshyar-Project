from django import forms
from LessonsApp.models import lesson_class, lesson
import jdatetime

class LessonClassFrom(forms.ModelForm):
    exam_date_time = forms.CharField(label="تاریخ و زمان امتحان", 
                                    widget=forms.TextInput(attrs={
                                                        'placeholder': 'YYYY-MM-DDTHH:MM',
                                                        'class':'datetime-input'
                                                        }),
                                    help_text="eg: 1404-06-09T15:05",
                                    error_messages={"required":"این فیلد اجباری است"}
                                )
    class Meta:
        model = lesson_class
        fields = "__all__"
        exclude = ['created', 'modified', '']

        help_texts = {
            "class_start_time":"AM/PM 09:05 :مثال",
            "class_end_time":"AM/PM 13:25 :مثال",
        }

        widgets = {
            "class_start_time":forms.TimeInput(
                attrs={'type': 'time'},
                format='%H:%M'
            ),

            "class_end_time":forms.TimeInput(
                attrs={'type': 'time'},
                format='%H:%M'
            ),

            "semester":forms.TextInput(
                attrs={
                    "readonly":True
                }
            )
        }

    def clean(self):
        clean_date = super().clean()
        start_time = clean_date.get("class_start_time")
        end_time = clean_date.get("class_end_time")
        exam_date_time = clean_date.get("exam_date_time")
        
        if start_time == end_time:
            raise forms.ValidationError("ساعت شروع و پایان نمی توانند یکسان باشند")
        
        if exam_date_time is not None:
            if len(exam_date_time) != 16:
                self.add_error("exam_date_time","باشد yyyy/mm/ddThh:mm تاریخ و زمان باید به فرمت")
                return clean_date
        
            try:
                exam_year = int(exam_date_time[:4])
                exam_month = int(exam_date_time[5:7])
                exam_day = int(exam_date_time[8:10])
                exam_hour = int(exam_date_time[11:13])
                exam_minute = int(exam_date_time[14:])
            except (ValueError, TypeError):
                self.add_error("exam_date_time","باشد yyyy/mm/ddThh:mm تاریخ و زمان باید به فرمت")
                return clean_date

            T_location = exam_date_time.find("T")
            if T_location != 10:
                self.add_error("exam_date_time","باشد yyyy/mm/ddThh:mm تاریخ و زمان باید به فرمت")
            
            if exam_year < jdatetime.date.today().year:
                self.add_error("exam_date_time", "سال امتحان نمی تواند از سال فعلی کمتر باشد")
            
            if not 1 <= exam_month <=12:
                self.add_error("exam_date_time", "ماه امتحان باید عددی بین 1 تا 12 باشد")
            
            if not 1 <= exam_day <= 31:
                self.add_error("exam_date_time", "روز امتحان باید عددی بین 1 تا 31 باشد")
            
            if not 7 <= exam_hour <= 20:
                self.add_error("exam_date_time", "ساعت امتحان باید عددی بین 7 تا 20 باشد")
            
            if not 0 <= exam_minute <= 59:
                self.add_error("exam_date_time", "دقیقه امتحان باید عددی بین 0 تا 59 باشد")
            
            if not self.errors.get("exam_date_time"):
                clean_date['exam_date_time'] = jdatetime.datetime(exam_year, exam_month, exam_day, exam_hour, exam_minute)
        
        return clean_date

    def save(self, commit=True):
        instance = super().save(commit=False)


        if commit:
            instance.save()
        
        return instance


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
                return clean_data

        
        # ? pishniaz and hamniaz validation
        for i in pishniaz.all():
            for j in hamniaz.all():
                if i == j:
                    self.add_error("pishniaz", "یک درس نمی تواند هم پیش نیاز باشد و هم همنیاز")
                    return clean_data
        
        # if apply_to_all:
        #     clean_data["lesson_major"] = major.objects.none()

    #def save(self, commit)