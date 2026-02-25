from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from .forms import *

# Create your views here.

@login_required(login_url=settings.LOGIN_URL)
def lesson_form_view(request):
    if request.method == "POST":
        form = LessonForm(request.POST)

        if form.is_valid():
            new_lesson = form.save(commit=False)
            set_lesson_code(lesson, new_lesson)

            new_lesson.save()
            new_lesson.pishniaz.set(form.cleaned_data["pishniaz"])
            new_lesson.hamniaz.set(form.cleaned_data["hamniaz"])
            form.save_m2m()

            messages.success(request, "ثبت درس موفقیت آمیز بود")
            return redirect('academic:main')
        
    else:
        form = LessonForm()
    
    return render(request, "register_lesson.html", {'form':form})



@login_required(login_url=settings.LOGIN_URL)
def lesson_class_form_view(request):
    if request.method == "POST":
        form = LessonClassFrom(request.POST)
        #flag = False

        if form.is_valid():
            new_lesson_class = form.save(commit=False)
            day = form.cleaned_data["class_day"]
            start_time = form.cleaned_data["class_start_time"]
            end_time = form.cleaned_data["class_end_time"]
            class_number = form.cleaned_data["class_number"]
            semester = form.cleaned_data["semester"]
            class_location = form.cleaned_data["university_location"]

            if semester == None or semester == " ":
                set_semester(lesson_class, new_lesson_class)
                semester = new_lesson_class.semester


            # ? checking class overlap
            classes = lesson_class.objects.filter(semester=semester,
                                                        class_day=day,
                                                        class_start_time=start_time,
                                                        class_end_time=end_time,
                                                        class_number=class_number,
                                                        university_location=class_location
                                                        )
            if classes:
                form = LessonClassFrom(request.POST)
                messages.error(request, f"زمان و روز برگزاری این کلاس با  {classes[0]}  تداخل دارد")
                return render(request, "add_lesson_class.html", {'form':form})
        
            # ? alternative way for checking class overlap
            #classes = lesson_class.objects.all()
            # for i in classes:
            #     if i.semester == semester:
            #         if i.class_day == day:
            #             if i.lesson_time == time:
            #                 if i.class_number == class_number:
            #                     flag = True
            
            # if not flag:
            #     form.save()
            #     messages.success(request, "کلاس با موفقیت ایجاد شد")
            #     return redirect("academic:main")
            # else:
            #     form = LessonClassFrom(request.POST)
            #     messages.error(request, "زمان و روز برگزاری این کلاس با یک کلاس دیگر تداخل دارد")
            #     messages.info(request, i)
            #     return render(request, "add_lesson_class.html", {'form':form})
            
            try:
                form.save(commit=True)
            except IntegrityError:
                messages.error(request, "این کد ارائه در این نیمسال وجود دارد")
                form = LessonClassFrom(request.POST)
                return render(request, "add_lesson_class.html", {'form':form})
            
            messages.success(request, "کلاس با موفقیت ایجاد شد")
            return redirect("academic:main")
        
    else:
        form = LessonClassFrom()

    return render(request, "add_lesson_class.html", {'form':form})