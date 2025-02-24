from django.shortcuts import render, HttpResponse

# Create your views here.


def home_view(request):
    # return HttpResponse('Hello World')
    return render(request, 'mainsite/home.html',)


def login(request):
    return render(request,'mainsite/login.html')


def registration(request):
    return render(request,'mainsite/registration.html')