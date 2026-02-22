from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.conf import settings
from ProfessorsApp.models import professor
from academic.models import university, group
from LessonsApp.models import lesson_class, lesson
from StudentsApp.models import student_choosing_lesson, student
from .forms import *
from .models import *
# Create your views here.

@login_required(login_url=settings.LOGIN_URL)
def professor_form_view(request):

    if request.method == "POST":
        form = ProfessorForm(request.POST, request.FILES)
        if form.is_valid():
            new_professor = form.save(commit=False)

            #set_created(professor, new_professor, created=True)
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
            return redirect('academic:main')
    else:
        form = ProfessorForm()

    return render(request, "register_professor.html", {"form":form})



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
        lesson_details.append((i.class_day, i.class_code))
    
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
                student_info = student.objects.get(student_number=i.cleaned_data["student_number"])
                submitted_score = i.cleaned_data["score"]

                Grade.objects.create(
                    student_name=student_info,
                    lesson_name=lesson_class_data,
                    score=submitted_score
                )
            messages.success(request, "ثبت نمره با موفقیت انجام شد")
            return redirect("academic:main")
        
    else:
        formset = GradeFormset(initial=initail_data)
    
    return render(request, "submittingGrade.html", {"formset":formset})