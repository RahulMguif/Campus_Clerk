from django.shortcuts import render
from student.models import *

# Create your views here.
def hod_home(request):
    return render(request,"hod/home.html")

def review_application(request):
    applications=student_application_request.objects.filter(staff_approval_status ='Approved')
    return render(request,"hod/review_application.html",{'applications':applications})