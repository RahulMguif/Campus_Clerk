from django.shortcuts import render

def admin_home(request):
    return render(request,"office_admin/home.html")
