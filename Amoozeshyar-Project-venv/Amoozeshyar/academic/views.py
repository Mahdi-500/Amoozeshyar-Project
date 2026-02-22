from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import *

# Create your views here.
@login_required(login_url=settings.LOGIN_URL)
def MainView(request):
    user = User.objects.get(username=request.user.username)
    user_group = user.groups.get()
    return render(request, "main.html", {"group":user_group, "user":user})
    


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
                    return redirect("academic:main")

                except Group.DoesNotExist:
                    messages.warning(request, "گروهی برای شما تعیین نشده است")
                    return redirect("academic:login")
            else:
                messages.warning(request, "نام کاربری یا رمز عبور صحیح نیست")
                return redirect("academic:login")
            
    else:
        form=LoginForm()

    return render(request, "Login.html", {'form':form})