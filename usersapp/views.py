from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import LoginForm
from django.contrib.auth import get_user_model, logout
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timesince import timesince
from django.utils import timezone


User = get_user_model()

class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "usersapp/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("home")  # بعد از لاگین کجا بره


def LogoutView(request):
    logout(request)
    return redirect("login")


class LastLoginView(APIView):
    def get(self, request):
        try:
            user = request.user
            last_login = user.last_login
            # print()
            # print(timezone.now())
            return Response({
                'username': user.username,
                'last_login': last_login.strftime("%Y-%m-%d %H:%M:%S"),
                'last_login_human': timesince(last_login, timezone.now()) + " ago"
            })
        except Exception as e:
            return Response({'error': str(e)})
