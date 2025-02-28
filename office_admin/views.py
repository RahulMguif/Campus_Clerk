from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from office_admin.models import *
from staff_advisor.models import *
from hod.models import *
from student.models import *
from mainsite.models import *


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


def add_staff_advisor(request):
  
    try:
        user_nme = request.session.get('user_nme')
        # if user_nme is None:    
        #     return redirect('error_404')
        department = departments.objects.filter(delete_status=0)  # Exclude deleted records
        if request.method == 'POST' and 'add' in request.POST:
            name = request.POST.get('name').strip()
            email = request.POST.get('email').strip()
            password= request.POST.get('password').strip()
            mobile= request.POST.get('mobile').strip()
            department_id=request.POST.get('department')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected
           
            staff = staff_advisor.objects.create(
                    name=name,
                    email=email,
                    password=password,
                    mobile=mobile,
                    is_active=1,
                    department_pk=department 
                    
                )

            # Create login entry for staff advisor
            department_login.objects.create(
                staff_advisor_pk=staff,
                role="staff_advisor",
                delete_status=False
            )

            messages.success(request, 'Successfully saved the staff advisor.')
            return redirect('add_staff_advisor')
        
        # Fetch all data from the database
        all_data = staff_advisor.objects.filter(delete_status=False).order_by('-id')  # Adjust filter as needed

        contexts = {
            'username': user_nme,
            'all_data': all_data,
            'department':department
        }
    
        return render(request,"office_admin/add_staff_advisor.html",contexts)

    except Exception as e:
        print('Exception in staff_advisor:', e)
        messages.error(request, 'An error occurred. Please contact admin.')
        return render(request,"office_admin/add_staff_advisor.html")
    



def edit_staff_advisor(request):
    if request.method == "POST":
        try:
            user_nme = request.session.get('user_nme')
            if user_nme is None:
                return redirect('error_404')
            
            admin_pk = request.POST.get("admin_pk")
            name = request.POST.get("name")
            email = request.POST.get("email")
            password = request.POST.get("password")
            mobile = request.POST.get("mobile")
            department_id=request.POST.get('department')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected

            entry = get_object_or_404(staff_advisor, pk=admin_pk)
            entry.name = name
            entry.email = email
            entry.password = password
            entry.mobile = mobile
            entry. department_pk=department 

            entry.save()
            messages.success(request, 'Updated Successfully.')

            return redirect('add_staff_advisor')

        except Exception as e:
            print('Exception in add_staff_advisor:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return render(request,"office_admin/add_staff_advisor.html")

    return redirect('add_staff_advisor')

def delete_staff_advisor(request):
    try:
        user_nme = request.session.get('user_nme')
        if user_nme is None:
            return redirect('error_404')
        
        print("POST data:", request.POST)
        admin_pk = request.POST.get('admin_pk')
        print("Received chat_id_pk:", admin_pk)
        # Check if staff_advisor exists
        main_admin_record = staff_advisor.objects.get(id=admin_pk)
        main_admin_record.delete_status = True
        main_admin_record.save()

        login_record = department_login.objects.filter(staff_advisor_pk=main_admin_record).first()
        if login_record:
            login_record.delete_status = True
            login_record.save()

        messages.success(request, 'Successfully deleted the staff advisor.')
        return redirect('add_staff_advisor')
    except main_admin_record.DoesNotExist:   
        messages.error(request, 'staff_advisor not found.')
        return redirect('add_staff_advisor')
    except Exception as e:
        # Handle other exceptions
        print('Exception delete_staff_advisor:', e)
        messages.error(request, 'An error occurred while deleting the staff_advisor. Please contact  admin.')
      
        return redirect('add_staff_advisor')



def change_admin_status(request, admin_pk):
    if request.method == 'POST':
        try:
          
            admin = get_object_or_404(staff_advisor, pk=admin_pk)
            status = request.POST.get('adminstatus')
            print(admin_pk)

            if status == 'Block':
                admin.is_active = 2  # Set is_active to 2 for blocking
                admin.save()
            if status == 'Allow':
                admin.is_active = 1  # Set is_active 
                admin.save()    
            
            messages.success(request, 'Successfully changed the status')
            return redirect('add_staff_advisor')  # Redirect after successfully updating status

        except Exception as e:
            print('Exception in change_admin_status:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return redirect('add_staff_advisor')  # Redirect to a safe page even on error

    else:
        return redirect('add_staff_advisor')  
    
def add_hod(request) :
    try:
        user_nme = request.session.get('user_nme')
        # if user_nme is None:
        #     return redirect('error_404')
        department = departments.objects.filter(delete_status=0)  # Exclude deleted records
        if request.method == 'POST' and 'add' in request.POST:
            name = request.POST.get('name').strip()
            email = request.POST.get('email').strip()
            password= request.POST.get('password').strip()
            mobile= request.POST.get('mobile').strip()
            department_id=request.POST.get('department')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected
           
           
            hod_data = hod.objects.create(
                    name=name,
                    email=email,
                    password=password,
                    mobile=mobile,
                    is_active=1,
                    department_pk=department 

                    
                )

            # Create login entry for staff advisor
            department_login.objects.create(
                hod_pk=hod_data,
                role="hod",
                delete_status=False
            )

            messages.success(request, 'Successfully saved the HOD.')
            return redirect('add_hod')
        
        # Fetch all data from the database
        all_data = hod.objects.filter(delete_status=False).order_by('-id')  # Adjust filter as needed

        contexts = {
            'username': user_nme,
            'all_data': all_data,
            'department':department
        }
    
        
        return render(request,'office_admin/add_hod.html',contexts)   

    except Exception as e:
        print('Exception in add_hod:', e)
        messages.error(request, 'An error occurred. Please contact admin.')
        return render(request,'office_admin/add_hod.html')   
    

def edit_hod(request):
    if request.method == "POST":
        try:
            user_nme = request.session.get('user_nme')
            if user_nme is None:
                return redirect('error_404')
            
            admin_pk = request.POST.get("admin_pk")
            name = request.POST.get("name")
            email = request.POST.get("email")
            password = request.POST.get("password")
            mobile = request.POST.get("mobile")
            department_id=request.POST.get('department')
            # Ensure the department exists before saving
            if department_id:
                department = departments.objects.get(id=department_id)  # Fetch the department object
            else:
                department = None  # Handle cases where no department is selected

            entry = get_object_or_404(hod, pk=admin_pk)
            entry.name = name
            entry.email = email
            entry.password = password
            entry.mobile = mobile
            entry. department_pk=department 


            entry.save()
            messages.success(request, 'Updated Successfully.')

            return redirect('add_hod')

        except Exception as e:
            print('Exception in add_hod:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return render(request,"office_admin/add_hod.html")

    return redirect('add_hod')

def delete_hod(request):
    try:
        user_nme = request.session.get('user_nme')
        if user_nme is None:
            return redirect('error_404')
        
        print("POST data:", request.POST)
        admin_pk = request.POST.get('admin_pk')
        print("Received chat_id_pk:", admin_pk)
        main_admin_record = hod.objects.get(id=admin_pk)
        main_admin_record.delete_status = True
        main_admin_record.save()

        login_record = department_login.objects.filter(hod_pk=main_admin_record).first()
        if login_record:
            login_record.delete_status = True
            login_record.save()

        messages.success(request, 'Successfully deleted the hod.')
        return redirect('add_hod')
    except main_admin_record.DoesNotExist:   
        messages.error(request, 'hod not found.')
        return redirect('add_hod')
    except Exception as e:
        # Handle other exceptions
        print('Exception delete_hod:', e)
        messages.error(request, 'An error occurred while deleting the hod. Please contact  admin.')
      
        return redirect('add_hod')



def change_status_hod(request, admin_pk):
    if request.method == 'POST':
        try:
          
            admin = get_object_or_404(hod, pk=admin_pk)
            status = request.POST.get('adminstatus')
            print(admin_pk)

            if status == 'Block':
                admin.is_active = 2  # Set is_active to 2 for blocking
                admin.save()
            if status == 'Allow':
                admin.is_active = 1  # Set is_active 
                admin.save()    
            
            messages.success(request, 'Successfully changed the status')
            return redirect('add_hod')  # Redirect after successfully updating status

        except Exception as e:
            print('Exception in change_admin_status:', e)
            messages.error(request, 'An error occurred. Please contact  admin.')
            return redirect('add_hod')  # Redirect to a safe page even on error

    else:
        return redirect('add_hod')  
    
    
def feedback_menu(request):
    if request.method == 'POST':
        id=request.POST.get('id')
        # return HttpResponse(id)
        select=request.POST.get('select_value')
        update=feedback_enable.objects.get(id=id)
        update.enable_status=select
        update.save()
        messages.success(request, 'Successfully changed the status')
        return redirect('feedback_menu')
    ids=1
    status=feedback_enable.objects.get(id=ids)
    context={'status':status}
    return render(request,"office_admin/feed_back_menu.html",context)
    
def view_applications(request):
    application_details = student_application_request.objects.filter(hod_approval_status='Approved').order_by('-id')

    return render(request,'office_admin/view_applications.html',{'application_details':application_details})    


from django.core.files.storage import FileSystemStorage

def update_application(request, application_id):
    application_entry = get_object_or_404(student_application_request, id=application_id)

    if request.method == 'POST':
        office_remark = request.POST.get('office_remark', '')
        office_signature = request.FILES.get('office_signature')

        # Update office remark
        application_entry.office_remark = office_remark

        # Handle office signature file upload
        if office_signature:
            fs = FileSystemStorage(location='media/office_signatures/')
            filename = fs.save(office_signature.name, office_signature)
            application_entry.office_signature_url = f'media/office_signatures/{filename}'

        # Save changes
        application_entry.save()
        print("saved application")
        messages.success(request, "Application updated successfully!")
        return redirect('view_applications')  # Adjust based on your URL name

    return render(request, 'office_admin/update_application.html', {'application_entry': application_entry})

from django.utils.timezone import now


def approval_status_office(request, admin_pk):  # Changed application_id → admin_pk
    if request.method == "POST":
        application = get_object_or_404(student_application_request, pk=admin_pk)
        new_status = request.POST.get("adminstatus")  # Get status from form

        # Update application status and date
        application.office_approval_status = new_status
        application.office_approval_date = now()
        application.save()

        messages.success(request, "Application status updated successfully.")
        return redirect("view_applications")  # Redirect to the applications page

    messages.error(request, "Invalid request.")
    return redirect("view_applications")