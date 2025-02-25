from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout
from office_admin.models import office_admin



def admin_home(request):
    return render(request,"office_admin/home.html")

def office_admin_login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        if office_admin.objects.filter(username=username).exists():
            user_password = office_admin.objects.get(username=username).password
            if user_password == password:
                print('Existing User')
                request.session['user_nme'] = username
                request.session.set_expiry(0)
                return redirect('admin_home')
            else:
                print('Permission Denied By Super Admin, user_status == 0')
                messages.error(request, 'Permission Denied By Super Admin')
                return render(request, 'mguif_admin/login.html')
    return render(request,"office_admin/office_admin_login.html")


def logout_view(request):
    request.session.flush()  # Completely clears the session
    logout(request)  # Logs out the user
    return redirect('office_admin_login')  # Redirect to the login page (update as needed)


def course_config(request):
    if request.method=="POST":
        course=request.POST.get(course)
        return HttpResponse(course)
    return render(request,"office_admin/course_configuration.html")


def department_config(request):
    return render(request,"office_admin/department_configuration.html")