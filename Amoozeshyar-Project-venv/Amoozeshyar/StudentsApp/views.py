from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from Amoozeshyar.LessonsApp.models import lesson_class, lesson
from ProfessorsApp.models import Grade
from .forms import *
from .forms import semester as setting_semester
from .models import *

# Create your views here.
@login_required(login_url=settings.LOGIN_URL)
def student_form_view(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            new_student = form.save(commit=False)
            set_entrance_year(student, new_student)
            set_last_year(student, new_student, created=True)
            set_student_number(student, new_student)

            new_user = User.objects.create_user(
                first_name = form.cleaned_data["first_name"],
                last_name = form.cleaned_data["last_name"],
                username=new_student.student_number,
                password=str(new_student.date_of_birth)[:4]
            )
            new_student.user = new_user
            new_student.save()
            
            # ? adding a group
            if not Group.objects.filter(name='student').exists():
                Group.objects.create(name='student')

            student_group = Group.objects.get(name='student')
            new_student.user.groups.add(student_group)

            messages.success(request, "ثبت نام موفقیت آمیز بود")
            return redirect('academic:main')
        
    else:
        form = StudentForm()

    return render(request, "register_student.html", {"form":form})



@login_required(login_url=settings.LOGIN_URL)
def student_lesson_search_view(request):
    flag = False
    if request.method == "POST":
        flag = True
        form = StudentLessonSearchForm(data=request.POST)
        if form.is_valid():
            
            # ? decides to use which model for searching
            if form.cleaned_data["query_lesson_code"] != None:
                result = lesson_class.objects.filter(Q(lesson_code=form.cleaned_data["query_lesson_code"]) &
                                                    Q(semester=form.cleaned_data["query_lesson_semester"]))
            else:
                if form.cleaned_data["query_lesson_name"] != "":
                    lessons = lesson.objects.filter(Q(name__contains=form.cleaned_data["query_lesson_name"]) |
                                                    Q(unit_type=form.cleaned_data["query_unit_type"]) |
                                                    Q(lesson_type=form.cleaned_data["query_lesson_type"]))
                else:
                    lessons = lesson.objects.filter(Q(unit_type=form.cleaned_data["query_unit_type"]) |
                                                    Q(lesson_type=form.cleaned_data["query_lesson_type"]))
                
                result = []
                temp = []
                for i in lessons:
                    temp.append(lesson_class.objects.filter(Q(lesson_code=i.code) &
                                                                Q(semester=form.cleaned_data["query_lesson_semester"])))
                for i in temp:
                    for j in range(0, len(i)):
                        result.append(i[j])
            
            context = {
                "result":result, 
                "form":form,
                "flag":flag
            }
            return render(request, "lesson_search_result.html", context)

    else:
        form = StudentLessonSearchForm()

    return render(request, "lesson_search_result.html", {"form":form, "flag":flag})    



@login_required(login_url=settings.LOGIN_URL)
def choosing_lesson_form_view(request):


    if request.method == "POST":
        form_searching = StudentLessonSearchForm(data=request.POST)
        form_choosing = ChoosingLessonForm()

        result = []
        temp = []
        if form_searching.is_valid():
            
            student_info = student.objects.get(student_number=request.user.username)
            semester = int(setting_semester())
            data = {
                "name": form_searching.cleaned_data["query_lesson_name"],
                "code":form_searching.cleaned_data["query_lesson_code"],
                "unit_type":form_searching.cleaned_data["query_unit_type"],
                "lesson_type":form_searching.cleaned_data["query_lesson_type"],
                "lesson_major":student_info.major
            }

            filters = {
                key: value
                for key, value in data.items()
                if value is not None
            }
            temp = lesson.objects.filter(**filters)
            for i in temp:
                if i.classes.all().exists():
                    for j in range(0, len(i.classes.all())):
                        if i.classes.all()[j].semester == semester:
                            result.append(i.classes.all()[j])

            if result == []:
                flag = True
            else:
                flag = False
                choices = []
                for i in result:
                    choices.append((i.id,f"نام درس: {i.lesson_code.name}   ---   نام استاد: {i.professor_name}   ---   کد درس: {i.lesson_code.code}   ---   زمان برگزاری: {i.class_day} - {i.class_end_time} تا {i.class_start_time}"))

                form_choosing.fields["chosen_lesson"].choices = choices
                request.session['lesson_choices'] = choices
                request.session["semester"] = setting_semester()

                
            context = {
                "form_searching": form_searching,
                "form_choosing": form_choosing,
                "flag":flag
            }
            return render(request, "choosing_lesson.html", context)
    
    else:
        form_searching = StudentLessonSearchForm()

    return render(request, "lesson_search_result.html", {"form":form_searching})



# todo - this is for saving the chosen lesson in previous view
@login_required(login_url=settings.LOGIN_URL)
def saving_chosen_lesson_view(request):
    if request.method == "POST":
        choices = request.session.get("lesson_choices")
        form = ChoosingLessonForm(data=request.POST)
        form.fields["chosen_lesson"].choices = choices

        if form.is_valid():
            student_info = student.objects.get(student_number = request.user.username)
            class_info = lesson_class.objects.get(id=form.cleaned_data["chosen_lesson"])

            # if student_choosing_lesson.objects.filter(
            #     student_name=student_info,
            #     chosen_class=class_info,
            #     semester=request.session.get("semester")
            # ).exists():
            #     messages.warning(request, "این درس را قبلا برداشته اید")
            #     return redirect("academic:choosing_lesson")
            #else:
            try:
                student_choosing_lesson.objects.get(student_name=student_info, chosen_class=class_info, semester=request.session.get("semester"))
                messages.warning(request, "این درس را قبلا برداشته اید")    # ! warning

            except student_choosing_lesson.DoesNotExist:
                temp = student_choosing_lesson.objects.filter(student_name=student_info)
                flag = True
            

                # ? checking for duplicate lesson
                duplicate_flag = False
                for i in temp:
                    if i.chosen_class.lesson_code == class_info.lesson_code:
                        score = Grade.objects.filter(student_name=student_info, lesson_name=i.chosen_class).last()
                        if score >= 10:
                            duplicate_flag = True

                if duplicate_flag:
                    messages.error(request, "این درس را قبلا برداشته اید")  # ! error
                    return redirect("academic:choosin_lesson")
                
                

                # ? checking if the student has pssed the requirements for that lesson
                grade = ()
                flag_passed_pishniaz = '0'
                if class_info.lesson_code.pishniaz.all().exists():
                    for i in class_info.lesson_code.pishniaz.all():     # ? iterates on all of the lesson pishniazes
                        for j in student_choosing_lesson.objects.filter(student_name=student_info):     # ? finds the student
                            if j.chosen_class.lesson_code==i:   # ? check's if this is the class we are looking for by checking the lesson code
                                try:
                                    student_grade = Grade.objects.get(student_name=student_info, lesson_name=j.chosen_class).score

                                    if student_grade >= 10:
                                        flag_passed_pishniaz = '1'
                                    
                                    grade += tuple(flag_passed_pishniaz)
                                
                                except Grade.DoesNotExist:
                                    flag_passed_pishniaz = "1"
                                    pass
                
                confirmation_of_passed_all_pishniazes = True
                for i in range(0, len(grade) - 1):
                    confirmation_of_passed_all_pishniazes &= bool(grade[i])
                
                if not confirmation_of_passed_all_pishniazes:
                    messages.error(request, "ابتدا باید پیش نیاز درس را قبول بشوید")    # ! error
                    return redirect("academic:choosing_lesson")
                

                ### ? checking the maximum units allowed
                

                # ?? for summer semester
                semester = request.session.get("semester")
                max_unit = 8
                if semester[3] == "3":
                    flag = maximum_unit_allowed(request, student_info, class_info, max_unit)
                    if flag:
                        messages.error(request, f"تعداد واحد انتخابی از سقف تعداد واحد مجاز ({max_unit}) بیشتر است")    # ! error
                        return redirect("academic:choosing_lesson")
                    else:
                        student_choosing_lesson.objects.create(student_name=student_info,
                                                                chosen_class=class_info,
                                                                semester=request.session.get("semester"))
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("academic:choosing_lesson")


                # ?? for fall semester
                max_unit = 20
                if semester[3] == "1":
                    new_semester = str(int(semester) - 9)    # ? privious semester (spring)
                    try:
                        privious_semester_student_classes = student_choosing_lesson.objects.filter(student_name=student_info, semester=new_semester)
                        unit = 0
                        score = 0
                        for i in privious_semester_student_classes:
                            for j in Grade.objects.filter(student_name=student_info, lesson_name=i):
                                if j.score >= 10:
                                    score += j.score
                                    unit += j.lesson_name.lesson_code.unit

                        if score / unit >= 17.00:
                            max_unit = 24
                        
                    except student_choosing_lesson.DoesNotExist:
                        pass

                    flag = maximum_unit_allowed(request, student_info, class_info, max_unit)
                    if flag:
                        messages.error(request, f"تعداد واحد انتخابی از سقف تعداد واحد مجاز ({max_unit}) بیشتر است")    # ! error
                        return redirect("academic:choosing_lesson")
                    else:
                        student_choosing_lesson.objects.create(student_name=student_info,
                                                                chosen_class=class_info,
                                                                semester=request.session.get("semester"))
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("academic:choosing_lesson")
                    
                    
                # ?? for spring semester
                elif semester[3] == "2":
                    new_semester = str(int(semester) - 1)    # ? privious semester (spring)
                    try:
                        privious_semester_student_classes = student_choosing_lesson.objects.filter(student_name=student_info, semester=new_semester)
                        unit = 0
                        score = 0
                        for i in privious_semester_student_classes:
                            for j in Grade.objects.filter(student_name=student_info, lesson_name=i):
                                if j.score >= 10:
                                    score += j.score
                                    unit += j.lesson_name.lesson_code.unit

                        if score / unit >= 17.00:
                            max_unit = 24
                        
                    except student_choosing_lesson.DoesNotExist:
                        pass

                    flag = maximum_unit_allowed(request, student_info, class_info, max_unit)
                    if flag:
                        messages.error(request, f"تعداد واحد انتخابی از سقف تعداد واحد مجاز ({max_unit}) بیشتر است")    # ! error
                        return redirect("academic:choosing_lesson")

                    else:
                        student_choosing_lesson.objects.create(student_name=student_info,
                                                                chosen_class=class_info,
                                                                semester=request.session.get("semester"))
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("academic:choosing_lesson")
            
    return redirect("academic:choosing_lesson")




def maximum_unit_allowed(request, student_info, class_info, max_unit) -> bool:
    try:
        student_classes = student_choosing_lesson.objects.filter(student_name=student_info, semester=semester())
        overall_units = 0
        for i in student_classes:
            overall_units += i.chosen_class.lesson_code.unit


            if overall_units + class_info.lesson_code.unit > max_unit:
                return True

    except student_choosing_lesson.DoesNotExist:
        student_choosing_lesson.objects.create(student_name=student_info,
                                                            chosen_class=class_info,
                                                            semester=request.session.get("semester"))
    return False