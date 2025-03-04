from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def staff_incharge_home(request):
    return render(request,"staff_incharge/home.html")



def view_all_student(request):
    return render(request,"staff_incharge/view_students.html")


def incharge_add_student(request):
    return render(request,"staff_incharge/add_students.html")