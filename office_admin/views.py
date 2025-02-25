from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from office_admin.models import *
from staff_advisor.models import *


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


def add_staff_advisor(request):
  
    try:
        user_nme = request.session.get('user_nme')
        if user_nme is None:
            return redirect('error_404')
        
        if request.method == 'POST' and 'add' in request.POST:
            name = request.POST.get('name').strip()
            email = request.POST.get('email').strip()
            password= request.POST.get('password').strip()
            mobile= request.POST.get('mobile').strip()
           
            # try:
            #     # Validate username format
            #     validate_username(name)
            #     validate_email(email)
            #     validate_password(password)
            #     # Validate mobile number length for India
            #     if country_code == "91" and len(mobile) < 10:
            #         raise ValidationError("For India, the mobile number must be at least 10 digits.")
                
            #     # if main_admin.objects.filter(email=email).exists() or main_admin.objects.filter(mobile=phone_full_number).exists():
            #     #     raise ValidationError("Admin already exists with this email or mobile number.")
            #     if staff_advisor.objects.filter(
            #         (Q(email=email) | Q(mobile=phone_full_number)) & Q(delete_status=0)
            #     ).exists():
            #         raise ValidationError("Admin already exists with this email or mobile number.")

            
            # except ValidationError as ve:
            #     messages.error(request, str(ve.message))
            #     return redirect('add_main_admin')    

            # Save the new chat ID to the database
            staff_advisor.objects.create(
                name=name,
                email=email,
                password=password,
                mobile=mobile,
                is_active=1,

                
            )

            messages.success(request, 'Successfully saved the staff advisor.')
            return redirect('add_staff_advisor')
        
        # Fetch all data from the database
        all_data = staff_advisor.objects.filter(delete_status=False).order_by('-id')  # Adjust filter as needed

        contexts = {
            'username': user_nme,
            'all_data': all_data
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
            entry = get_object_or_404(staff_advisor, pk=admin_pk)
            entry.name = name
            entry.email = email
            entry.password = password
            entry.mobile = mobile

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
        main_admin_record = staff_advisor.objects.get(id=admin_pk)
        main_admin_record.delete_status = True
        main_admin_record.save()
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