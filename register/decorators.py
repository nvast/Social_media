from django.shortcuts import redirect


def unauthenticated_user(function):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/home/')
        else:
            return function(request, *args, **kwargs)
    return wrapper_func
