from django.shortcuts import render

# Create your views here.
def staff_home(request):
    return render(request,"staff_advisor/home.html")