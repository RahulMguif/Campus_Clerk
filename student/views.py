from django.shortcuts import render

# Create your views here.


def student_home(request):
    return render(request, 'student/home.html')

def application_form(request):
    return render(request, 'student/student_application_form.html')