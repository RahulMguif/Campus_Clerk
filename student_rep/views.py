from django.shortcuts import render

# Create your views here.
def student_rep_home(request):
    return render(request,'student_rep/home.html')