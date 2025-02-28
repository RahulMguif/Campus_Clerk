from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from  mainsite.models import *

from django.http import JsonResponse
from django.contrib.auth import logout
from office_admin.models import *


def home_view(request):
    # return HttpResponse('Hello World')
    return render(request, 'mainsite/home.html',)


#======================login function for student========================================

def login(request):
    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")  

        if not password:
            print("Password field is empty!")  # Debugging
            return render(request, "mainsite/login.html", {"error": "Password is missing."})

        try:
            student = student_registration.objects.get(email=email)
            print(f"Stored Password (Hashed): {student.password}")  # Debugging

            if check_password(password, student.password):
                request.session["student_id"] = student.id
                request.session["student_name"] = student.fullname
                request.session["student_email"] = student.email
                messages.success(request, "Login successful!")
                # return render(request, "student/home.html")
                return redirect('student_dashboard')

            else:
                messages.error(request, "Invalid email or password.")
                print("Password mismatch!")  # Debugging
        except student_registration.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            print("User does not exist!")  # Debugging

    return render(request, "mainsite/login.html")

#======================END login function for student========================================
#===================check already registered email and mobile================================
def check_user_existence(request):
    email = request.GET.get('email', None)
    mobile = request.GET.get('mobile', None)

    email_exists = student_registration.objects.filter(email=email).exists() if email else False
    mobile_exists = student_registration.objects.filter(mobile=mobile).exists() if mobile else False

    return JsonResponse({'email_exists': email_exists, 'mobile_exists': mobile_exists})

#===================END check already registered email and mobile================================
#========================== student registration=================================================

def registration(request):
    departments_list=departments.objects.filter(delete_status=0)
    courses=course.objects.filter(delete_status=0)
    if request.method == "POST":

        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        course_list = request.POST.get("course")
        department = request.POST.get("department")
        semester = request.POST.get("semester")
        year_of_joining = request.POST.get("year_of_joining")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
       
        # Validate required fields
        if not (fullname and email and mobile and course_list and department and semester and year_of_joining and password and confirm_password):
            messages.error(request, "All fields are required.")
            return render(request, "mainsite/registration.html")

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "mainsite/registration.html")

        # Hash the password before saving
        hashed_password = make_password(password)

        # Save to database
        student = student_registration(
            fullname=fullname,
            email=email,
            mobile=mobile,
            course=course_list,
            department=department,
            semester=semester,
            year_of_joining=year_of_joining,
            password=hashed_password,
            is_active=True  
        )
        student.save()

        messages.success(request, "Registration successful!")
        return redirect("login")  

    return render(request, "mainsite/registration.html", { 'departments_list': departments_list,'courses':courses})

#==========================END student registration===============================================


def user_logout(request):
    request.session.flush()  # Completely clears the session
    logout(request)  # Logs out the user
    messages.success(request, "Logout successful!")
    return redirect('home')  # Redirect to the login page (update as needed)



def department_user_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        print("email", email)

        try:
            # Check if the user exists in the department_login table
            user_login = department_login.objects.select_related('hod_pk', 'staff_advisor_pk').filter(
                hod_pk__email=email, delete_status=False
            ).first() or department_login.objects.select_related('hod_pk', 'staff_advisor_pk').filter(
                staff_advisor_pk__email=email, delete_status=False
            ).first()

            print("user_login:", user_login)

            if not user_login:
                messages.error(request, 'No account found with this email.')
                return redirect('home')

            # Identify the user and check the password
            if user_login.hod_pk:
                user = user_login.hod_pk
                role = "hod"
            else:
                user = user_login.staff_advisor_pk
                role = "staff_advisor"

            # Check if the account is blocked
            if user.is_active == 2:
                messages.error(request, 'Your account has been blocked. Please contact the administrator.')
                return redirect('home')

            if user.password == password:  # Check password (Consider hashing for security)
                request.session['username'] = email
                request.session['role'] = role  # Store role in session
                request.session.set_expiry(0)

                if role == "hod":
                    return redirect('hod_home')
                else:
                    return redirect('staff_home')
            else:
                messages.error(request, 'Invalid password.')
                return redirect('home')

        except Exception as e:
            print('Exception in department_user_login:', e)
            messages.error(request, 'An error occurred during login. Please try again.')
            return redirect('home')

    return render(request, "mainsite/department_login.html")