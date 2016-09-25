from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http.response import Http404

class RegisterView(TemplateView):
    """description of class"""
    template_name = "SquareVeg/register.html"

    def post(self, request, *args, **kwargs):

        try:
            firstname = request.POST.get('firstname','')
            lastname = request.POST.get('lastname','')
            password = request.POST.get('password','')
            email = request.POST.get('email','')

            user = User.objects.create_user(email,email,password)
            user.last_name = lastname
            user.first_name = firstname
            user.save()
        except:
            return (request,'SquareVeg/register.html')

        return render(request,'SquareVeg/register.html')

    def get(self, request, *args, **kwargs):
        # super(RegisterView, self).get(request, *args, **kwargs)
        return render(request,'SquareVeg/register.html') 

class LoginView(TemplateView):
    template_name = "SquareVeg/login.html"

    def get(self, request, *args, **kwargs):
        # super(RegisterView, self).get(request, *args, **kwargs)
        return render(request,'SquareVeg/login.html') 

    def post(self, request, *args, **kwargs):

        try:
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page.
            else:
                Http404("Login Failed !!!")
        except:
            raise Http404("Invalid User")
