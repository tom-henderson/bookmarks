from django.shortcuts import redirect
from django.contrib.auth import logout


def log_out(request):
    logout(request)
    return redirect('/login')
