from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from .forms import *
from .forms import semester as setting_semester

# Create your views here.
@login_required(login_url=settings.LOGIN_URL)
def MainView(request):
    user = User.objects.get(username=request.user.username)
    user_group = user.groups.get()
    return render(request, "main.html", {"group":user_group, "user":user})



@login_required(login_url=settings.LOGIN_URL)
def student_form_view(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            new_student = form.save(commit=False)
            set_entrance_year(student, new_student)
            set_last_year(student, new_student)
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
            return redirect('website:main')
        
    else:
        form = StudentForm()

    return render(request, "register_student.html", {"form":form})



@login_required(login_url=settings.LOGIN_URL)
def professor_form_view(request):

    if request.method == "POST":
        form = ProfessorForm(request.POST, request.FILES)
        if form.is_valid():
            new_professor = form.save(commit=False)

            set_created(professor, new_professor)
            set_professor_code(professor, new_professor)


            new_user = User.objects.create_user(
                first_name = form.cleaned_data["first_name"],
                last_name = form.cleaned_data["last_name"],
                username = new_professor.code,
                password=str(form.cleaned_data["date_of_birth"])[:4]
            )


            new_professor.user = new_user
            new_professor.save()
            new_professor.universities.set(form.cleaned_data["universities"])

            # ? adding a group
            if not Group.objects.filter(name='professor').exists():
                Group.objects.create(name='professor')

            professor_group = Group.objects.get(name='professor')
            new_professor.user.groups.add(professor_group)
            
            messages.success(request, "ثبت نام موفقیت آمیز بود")
            return redirect('website:main')
    else:
        form = ProfessorForm()

    return render(request, "register_professor.html", {"form":form})



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

            messages.success(request, "ثبت درس موفقیت آمیز بود")
            return redirect('website:main')
        
    else:
        form = LessonForm()
    
    return render(request, "register_professor.html", {'form':form})



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
                                                        lesson_day=day,
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
            #         if i.lesson_day == day:
            #             if i.lesson_time == time:
            #                 if i.class_number == class_number:
            #                     flag = True
            
            # if not flag:
            #     form.save()
            #     messages.success(request, "کلاس با موفقیت ایجاد شد")
            #     return redirect("website:main")
            # else:
            #     form = LessonClassFrom(request.POST)
            #     messages.error(request, "زمان و روز برگزاری این کلاس با یک کلاس دیگر تداخل دارد")
            #     messages.info(request, i)
            #     return render(request, "add_lesson_class.html", {'form':form})
            
            try:
                form.save()
            except IntegrityError:
                messages.error(request, "این کد ارائه در این نیمسال وجود دارد")
                form = LessonClassFrom(request.POST)
                return render(request, "add_lesson_class.html", {'form':form})
            
            messages.success(request, "کلاس با موفقیت ایجاد شد")
            return redirect("website:main")
        
    else:
        form = LessonClassFrom()

    return render(request, "add_lesson_class.html", {'form':form})
    


def login_form_view(request):

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user is not None:
                try:
                    user.groups.get()
                    login(request, user)
                    request.user = user
                    messages.success(request, "وارد شدید")
                    return redirect("website:main")

                except Group.DoesNotExist:
                    messages.warning(request, "گروهی برای شما تعیین نشده است")
                    return redirect("website:login")
            else:
                messages.warning(request, "نام کاربری یا رمز عبور صحیح نیست")
                return redirect("website:login")
            
    else:
        form=LoginForm()

    return render(request, "Login.html", {'form':form})
    
    

@login_required(login_url=settings.LOGIN_URL)
def professor_profile_view(request):
    username = User.objects.get(username=request.user.username)
    professor_name = username.professor
    p_university_list = professor_name.universities.all()

    context = {
        "professor":professor_name,
        "p_university":p_university_list,
    }
    return render(request, "professor/profile.html", context)



@login_required(login_url=settings.LOGIN_URL)
def professor_lesson_list_view(request, p_code, u_code):
    professor_name = professor.objects.get(code=p_code)
    l_university = university.objects.get(code=u_code)
    temp_lesson_list = professor_name.classes.all()
    
    seen = set()
    lesson_list = []
    for i in temp_lesson_list:
        if i.lesson_code in seen:
            continue
        else:
            lesson_list.append(i)
            seen.add(i.lesson_code)
    request.session['p_code'] = p_code
    context = {
        "list":lesson_list,
        "l_university":l_university,
    }

    return render(request, "professor/professor_lesson_list.html", context)



@login_required(login_url=settings.LOGIN_URL)
def professor_lesson_details(request, l_code):
    professor_name = professor.objects.get(code=request.session["p_code"])
    assigned_lessons = lesson_class.objects.filter(lesson_code=l_code, professor_name=professor_name)
    lesson_details = []
    for i in assigned_lessons:
        lesson_details.append((i.lesson_day, i.class_code))
    
    context = {
        "lesson":lesson_details,
        "l_code":l_code,
    }
    return render(request, "lesson_details.html", context)
    


@login_required(login_url=settings.LOGIN_URL)
def grade_form_view(request, l_code, class_code):
    initail_data = []
    student_data = {}
    professor_name = professor.objects.get(code=request.session["p_code"])
    lesson_info = lesson.objects.get(code=l_code)
    lesson_class_data = lesson_class.objects.get(lesson_code=lesson_info, professor_name=professor_name, class_code=class_code)
    
    for j in student_choosing_lesson.objects.filter(chosen_class=lesson_class_data):
            
        student_data = {
            "first_name":j.student_name.first_name,
            "last_name":j.student_name.last_name,
            "student_number":j.student_name.student_number,
            "score":0
        }
        initail_data.append(student_data)


    if request.method == "POST":
        formset = GradeFormset(data=request.POST)
        
        if formset.is_valid():
            for i in formset:
                student_info = student.objects.get(student_number=i.cleaned_data["student_id"])
                submitted_score = i.cleaned_data["score"]

                Grade.objects.create(
                    student_name=student_info,
                    lesson_name=lesson_class_data,
                    score=submitted_score
                )
            messages.success(request, "ثبت نمره با موفقیت انجام شد")
            return redirect("website:main")
        
    else:
        formset = GradeFormset(initial=initail_data)
        return render(request, "submittingGrade.html", {"formset":formset})



@login_required(login_url=settings.LOGIN_URL)
def lesson_search_view(request):
    flag = False
    if request.method == "POST":
        flag = True
        form = LessonSearchForm(data=request.POST)
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
        form = LessonSearchForm()

    return render(request, "lesson_search_result.html", {"form":form, "flag":flag})    



@login_required(login_url=settings.LOGIN_URL)
def choosing_lesson_form_view(request):


    if request.method == "POST":
        form_searching = LessonSearchForm(data=request.POST)
        form_choosing = ChoosingLessonForm()

        result = []
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
                    choices.append((i.id,f"نام درس: {i.lesson_code.name}   ---   نام استاد: {i.professor_name}   ---   کد درس: {i.lesson_code.code}   ---   زمان برگزاری: {i.lesson_day} - {i.class_end_time} تا {i.class_start_time}"))

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
        form_searching = LessonSearchForm()

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
            #     return redirect("website:choosing_lesson")
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
                    return redirect("website:choosin_lesson")
                
                

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
                    return redirect("website:choosing_lesson")
                

                ### ? checking the maximum units allowed
                

                # ?? for summer semester
                semester = request.session.get("semester")
                max_unit = 8
                if semester[3] == "3":
                    flag = maximum_unit_allowed(request, student_info, class_info, max_unit)
                    if flag:
                        messages.error(request, f"تعداد واحد انتخابی از سقف تعداد واحد مجاز ({max_unit}) بیشتر است")    # ! error
                        return redirect("website:choosing_lesson")
                    else:
                        student_choosing_lesson.objects.create(student_name=student_info,
                                                                chosen_class=class_info,
                                                                semester=request.session.get("semester"))
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("website:choosing_lesson")


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
                        return redirect("website:choosing_lesson")
                    else:
                        student_choosing_lesson.objects.create(student_name=student_info,
                                                                chosen_class=class_info,
                                                                semester=request.session.get("semester"))
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("website:choosing_lesson")
                    
                    
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
                        return redirect("website:choosing_lesson")

                    else:
                        student_choosing_lesson.objects.create(student_name=student_info,
                                                                chosen_class=class_info,
                                                                semester=request.session.get("semester"))
                        messages.success(request, "درس با موفقیت انتخاب شد")    # + success
                        return redirect("website:choosing_lesson")
            
    return redirect("website:choosing_lesson")




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



@login_required(login_url=settings.LOGIN_URL)
def student_grade_history(request):
    pass