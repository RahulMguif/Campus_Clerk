from django.shortcuts import render, redirect
from staff_advisor.models import *
from django.contrib import messages

# Create your views here.
def staff_home(request):
    return render(request,"staff_advisor/home.html")

