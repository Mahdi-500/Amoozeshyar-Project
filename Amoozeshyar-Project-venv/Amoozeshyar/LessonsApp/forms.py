from django import forms
from LessonsApp.models import lesson_class, lesson

class LessonClassFrom(forms.ModelForm):
    class Meta:
        model = lesson_class
        fields = "__all__"
        exclude = ['created', 'modified']

        help_texts = {
            "class_start_time":"مثال: 09:05",
            "class_end_time":"مثال: 13:25",
        }

        error_messages = {
            "class_start_time":{"invalid":"باشد HH:MM زمان باید به فرمت",
                                "invalid_time":"ساعت باید 0 تا 23 و دقیقه باید بین 0 تا 59 باشد"},
            "class_end_time":{"invalid":"باشد HH:MM زمان باید به فرمت",
                                "invalid_time":"ساعت باید 0 تا 23 و دقیقه باید بین 0 تا 59 باشد"}
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
        
        if start_time == end_time:
            raise forms.ValidationError("ساعت شروع و پایان نمی توانند یکسان باشند")
        
        # start_index = [i for i,x in enumerate(start_time) if x == ":"]
        # end_index = [i for i,x in enumerate(end_time) if x == ":"]
        # flag = False

        # if len(start_index) != 1:
        #     self.add_error("class_start_time", "فقط یک ':' مجاز است")
        #     flag = True
        
        # if len(end_index) != 1:
        #     self.add_error("class_end_time", "فقط یک ':' مجاز است")
        #     flag = True

        # if not flag:
        #     start_time = start_time.replace(":", "")
        #     end_time = end_time.replace(":","")
            
            
        #     if len(start_time) != 4:
        #         self.add_error("class_start_time", "عدد ها را مانند مثال های داده شده وارد کنید")

        #     elif not 0 <= int(start_time) <= 2359:
        #         self.add_error("class_start_time","ساعت باید عددی بین 1 تا 23 و دقیقه باید عددی بین 0 تا 59 باشد")
            
        #     if len(end_time) != 4:
        #         self.add_error("class_end_time", "عدد ها را مانند مثال های داده شده وارد کنید")
            
        #     elif not 0 <= int(end_time) <= 2359:
        #         self.add_error("class_end_time","ساعت باید عددی بین 1 تا 23 و دقیقه باید عددی بین 0 تا 59 باشد")


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