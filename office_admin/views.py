from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout
from office_admin.models import course, departments, office_admin



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
        course_name=request.POST.get('course')
        add=course()
        add.course_name=course_name
        add.save()
        messages.success(request,'Successfully Added')
        return redirect('course_config')
    table=course.objects.filter(delete_status=0)
    context={'table':table}
    return render(request,"office_admin/course_configuration.html",context)


def department_config(request):
    if request.method=='POST':
        select=request.POST.get('select_name')
        branch=request.POST.get('branch')
        obj=departments()
        obj.department_name=branch
        obj.course_pk=course.objects.get(id=select)
        obj.save()
        messages.success(request,'Successfully Added')
        return redirect('department_config')
    cour = course.objects.filter(delete_status=0)
    table = departments.objects.filter(delete_status=0)
    context={'course':cour,'table':table}
    return render(request,"office_admin/department_configuration.html",context)


def department_delete(request):
    if request.method=='POST':
        id=request.POST.get('deletepackageid')
        delete=departments.objects.get(id=id)
        delete.delete_status=1
        delete.save()
        messages.success(request,'Delete Successfully')
        return redirect('department_config')
    
    
def course_delete(request):
    if request.method=='POST':
        id=request.POST.get('deletepackageid')
        delete=course.objects.get(id=id)
        delete.delete_status=1
        delete.save()
        messages.success(request,'Delete Successfully')
        return redirect('course_config')