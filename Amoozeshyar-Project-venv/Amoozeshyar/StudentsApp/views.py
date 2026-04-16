from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from LessonsApp.models import lesson_class, lesson
from ProfessorsApp.models import Grade
from .forms import *
from .forms import semester as set_semester
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
            filter_options = {}
            query_options = ["query_lesson_name", "query_unit_type", "query_lesson_type"]
            if form.cleaned_data["query_lesson_code"] is not None:
                result = lesson_class.objects.filter(Q(lesson_code=form.cleaned_data["query_lesson_code"]) &
                                                    Q(semester=form.cleaned_data["query_lesson_semester"]))
            else:
                for i,j in form.data.items():
                    if i in query_options and (j is not None and j != ""):
                        if i == "query_lesson_name":
                            key = "name"
                        elif i == "query_unit_type":
                            key = "unit_type"
                        elif i == "query_lesson_type":
                            key = "lesson_type"
                        
                        filter_options[key] = j
                
                lessons = lesson.objects.filter(**filter_options)

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
    chosen_classes = showing_the_chosen_lesson_before_saving(class_info_id=request.session['chosen_classes'])
    print(request.path == "/choosing_lesson")

    if request.method == "POST":
        form_searching = StudentLessonSearchForm(data=request.POST)

        result = []
        temp = []
        if form_searching.is_valid():

            student_info = student.objects.get(student_number=request.user.username)
            semester = int(set_semester())
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
                available_classes = {}
                loop_couner = 1
                for i in result:
                    available_classes[loop_couner] = [i.id, i.lesson_code.name, i.professor_name, i.lesson_code.code, i.class_day, f"{i.class_end_time} تا {i.class_start_time}"]
                    loop_couner += 1

                request.session["semester"] = set_semester()

            

            context = {
                "form_searching": form_searching,
                "available_classes":available_classes,
                "flag":flag,
                "chosen_classes":chosen_classes
            }
            return render(request, "choosing_lesson.html", context)
    
    else:
        form_searching = StudentLessonSearchForm()

    return render(request, "lesson_search_result.html", {"form":form_searching, "chosen_classes":chosen_classes})



def showing_the_chosen_lesson_before_saving(class_info_id):
    chosen_classes = {}
    loop_couner = 1
    for i in class_info_id:
        obj = lesson_class.objects.get(id=i)
        chosen_classes[loop_couner] = [obj.lesson_code.name, obj.professor_name, obj.lesson_code.code, 
                                        obj.class_day, f"{obj.class_end_time} تا {obj.class_start_time}"]
        loop_couner += 1
    
    return chosen_classes



# todo - the function saves the chosen lessons in session temporarely
@login_required(login_url=settings.LOGIN_URL)
def temporarely_saving_chosen_lesson_view(request):
    if request.method == "POST":
        form = ChoosingLessonForm(data=request.POST)
        form.fields["chosen_class"].choices = [(request.POST.get("chosen_class"), "the chosen class")]

        if form.is_valid():
            student_info = student.objects.get(student_number = request.user.username)
            class_info = lesson_class.objects.get(id=form.cleaned_data["chosen_class"])
            request.session['chosen_classes'] = []

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
                        mark = Grade.objects.filter(student_name=student_info, lesson_name=i.chosen_class).last().mark
                        if mark >= 10:
                            duplicate_flag = True

                if duplicate_flag:
                    messages.error(request, "این درس را قبلا برداشته اید")  # ! error
                    return redirect("student:choosing_lesson")
                

                status = check_lesson_requirements_status(class_info, student_info)
                if not status:
                    messages.error(request, "ابتدا باید پیش نیاز درس را قبول بشوید")    # ! error
                    return redirect("student:choosing_lesson")
                

                ### ? checking the maximum units allowed
                

                # ?? for summer semester
                semester = request.session.get("semester")
                max_unit = 8
                if semester[3] == "3":
                    flag = maximum_unit_allowed(request, student_info, class_info, max_unit)
                    if flag:
                        messages.error(request, f"تعداد واحد انتخابی از سقف تعداد واحد مجاز ({max_unit}) بیشتر است")    # ! error
                        return redirect("student:choosing_lesson")
                    else:
                        request.session['chosen_classes'].append(class_info.id)
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("student:choosing_lesson")


                # ?? for fall semester
                max_unit = 20
                if semester[3] == "1":
                    new_semester = str(int(semester) - 9)    # ? privious semester (spring)
                    try:
                        privious_semester_student_classes = student_choosing_lesson.objects.filter(student_name=student_info, semester=new_semester)
                        unit = 0
                        mark = 0
                        for i in privious_semester_student_classes:
                            for j in Grade.objects.filter(student_name=student_info, lesson_name=i):
                                if j.mark >= 10:
                                    mark += j.mark
                                    unit += j.lesson_name.lesson_code.unit

                        if mark / unit >= 17.00:
                            max_unit = 24
                        
                    except student_choosing_lesson.DoesNotExist:
                        pass

                    flag = maximum_unit_allowed(request, student_info, class_info, max_unit)
                    if flag:
                        messages.error(request, f"تعداد واحد انتخابی از سقف تعداد واحد مجاز ({max_unit}) بیشتر است")    # ! error
                        return redirect("student:choosing_lesson")
                    else:
                        request.session['chosen_classes'].append(class_info.id)
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("student:choosing_lesson")
                    
                    
                # ?? for spring semester
                elif semester[3] == "2":
                    new_semester = str(int(semester) - 1)    # ? privious semester (spring)
                    try:
                        privious_semester_student_classes = student_choosing_lesson.objects.filter(student_name=student_info, semester=new_semester)
                        unit = 0
                        mark = 0
                        for i in privious_semester_student_classes:
                            for j in Grade.objects.filter(student_name=student_info, lesson_name=i):
                                if j.mark >= 10:
                                    mark += j.mark
                                    unit += j.lesson_name.lesson_code.unit

                        if unit != 0:
                            if mark / unit >= 17.00:
                                max_unit = 24
                        
                    except student_choosing_lesson.DoesNotExist:
                        pass

                    flag = maximum_unit_allowed(request, student_info, class_info, max_unit)
                    if flag:
                        messages.error(request, f"تعداد واحد انتخابی از سقف تعداد واحد مجاز ({max_unit}) بیشتر است")    # ! error
                        return redirect("student:choosing_lesson")

                    else:                        
                        request.session['chosen_classes'].append(class_info.id)
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("student:choosing_lesson")
            
    return redirect("student:choosing_lesson")



@login_required(login_url=settings.LOGIN_URL)
def submiting_the_chosen_lesson(request):
    student_info = student.objects.get(student_number = request.user.username)
    class_info_id = request.session['chosen_classes']
    for i in class_info_id:
        class_info = lesson_class.objects.get(id=i)
        student_choosing_lesson.objects.create(student_name=student_info,
                                                chosen_class=class_info,
                                                semester=request.session.get("semester"))
    messages.success(request, "درس های انتخابی با موفقیت ذخیره شدند")   # + success
    return redirect("student:choosing_lesson")



@login_required(login_url=settings.LOGIN_URL)
def student_report_view(request):
    student_info = student.objects.get(student_number = request.user.username)
    semester_list = student_info.lessons.all().values_list("semester").distinct("semester")
    
    lesson_report = {}
    semester_status = {}
    overall_average = 0
    overall_units = 0
    for i in semester_list:
        score = 0
        total_units = 0
        average = 0
        lesson_name = student_choosing_lesson.objects.filter(student_name=student_info, semester=i[0])
        for j in lesson_name:
            try:
                lesson_mark = j.chosen_class.grade.get(student_name=student_info).mark
            except Grade.DoesNotExist:
                lesson_mark = "No mark yet"
            lesson_report.setdefault(i[0], []).append((j, lesson_mark))

            # ? calculating score, credit and average
            if lesson_mark != "No mark yet":
                score += (lesson_mark * j.chosen_class.lesson_code.unit)
                total_units += j.chosen_class.lesson_code.unit
        try:
            average = score / total_units
        except ZeroDivisionError:
            pass
        overall_average += average   
        overall_units += total_units

        semester_status.setdefault(i[0], []).append((score, total_units, average))

    overall_average /= len(semester_list)

    lesson_type_status = student_lesson_type_status(request)

    context = {
        "lesson_report":lesson_report,
        "semester_status":semester_status,
        "lesson_type_status":lesson_type_status,
        "overall_average":overall_average,
        "overall_units":overall_units
    }

    return render(request, "student_report.html", context)



def student_lesson_type_status(request) -> dict:
    student_info = student.objects.get(student_number=request.user.username)
    student_lesson_type_status = {
        "اصلی":0,
        "پایه":0,
        "عمومی":0,
        "تخصصی":0,
        "اختیاری":0,
    }
    for i in student_info.lessons.select_related("chosen_class").all():
        student_lesson_type_status[i.chosen_class.lesson_code.lesson_type] += i.chosen_class.lesson_code.unit
    return student_lesson_type_status

"""
todo - these function are for validating different things before a student can choose a class
"""
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


def check_lesson_requirements_status(class_info, student_info) -> bool:
    student_classes = ""
    requirements = ""
    passed = True
    try:
        requirements = class_info.lesson_code.pishniaz.all()
    except lesson.DoesNotExist:
        return passed
    
    # ? if lesson has no requirements
    if len(requirements) == 0:
        return True
    else:
        for i in requirements:
            # ? if the student had this lesson before or not
            try:
                student_classes = student_info.lessons.filter(chosen_class=i.code)
            except student_choosing_lesson.DoesNotExist:
                pass

        if not student_classes:
            return False
        else:
            for i in student_classes:
                latest_lesson_status = Grade.objects.filter(student_name=student_info, lesson_name=i.chosen_class.lesson_code)
                if latest_lesson_status.mark >= 10:
                    passed &= True
                else:
                    passed &= False
            
    return passed

def testview(request):
    print("hello world")