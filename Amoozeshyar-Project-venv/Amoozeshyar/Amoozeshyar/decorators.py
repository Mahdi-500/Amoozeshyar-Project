from django.contrib.auth.models import User
from functools import wraps
from django.shortcuts import render

def is_user_authorized(role_name="None"):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_info = User.objects.get(username=request.user.username)
            user_group_info = user_info.groups.get()
            if str(user_group_info) == role_name:
                response = view_func(request, *args, **kwargs)
                return response
            else:
                return render(request, "forbidden.html")
        return wrapper
    return decorator