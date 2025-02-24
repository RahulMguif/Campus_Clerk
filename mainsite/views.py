from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from  mainsite.models import *


def home_view(request):
    # return HttpResponse('Hello World')
    return render(request, 'mainsite/home.html',)


from django.contrib.auth.hashers import check_password
# def login(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")

#         print(f"Email: {email}, Password: {password}")  # Debugging

#         try:
#             student = student_registration.objects.get(email=email)
#             print(f"Stored Password (Hashed): {student.password}")  # Debugging

#             if check_password(password, student.password):
#                 request.session["student_id"] = student.id
#                 request.session["student_name"] = student.fullname
#                 messages.success(request, "Login successful!")
#                 return render(request, "student/home.html")

#             else:
#                 messages.error(request, "Invalid email or password.")
#                 print("Password mismatch!")  # Debugging
#         except student_registration.DoesNotExist:
#             messages.error(request, "Invalid email or password.")
#             print("User does not exist!")  # Debugging

#     return render(request, "mainsite/login.html")

def login(request):
    if request.method == "POST":
        print(f"Request POST Data: {request.POST}")  # Debugging

        email = request.POST.get("email")
        password = request.POST.get("password")  # Ensure 'password' is used, not 'pass'

        print(f"Email: {email}, Password: {password}")  # Debugging

        if not password:
            print("Password field is empty!")  # Debugging
            return render(request, "mainsite/login.html", {"error": "Password is missing."})

        try:
            student = student_registration.objects.get(email=email)
            print(f"Stored Password (Hashed): {student.password}")  # Debugging

            if check_password(password, student.password):
                request.session["student_id"] = student.id
                request.session["student_name"] = student.fullname
                messages.success(request, "Login successful!")
                return render(request, "student/home.html")

            else:
                messages.error(request, "Invalid email or password.")
                print("Password mismatch!")  # Debugging
        except student_registration.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            print("User does not exist!")  # Debugging

    return render(request, "mainsite/login.html")


def registration(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        course = request.POST.get("course")
        department = request.POST.get("department")
        semester = request.POST.get("semester")
        year_of_joining = request.POST.get("year_of_joining")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validate required fields
        if not (fullname and email and mobile and course and department and semester and year_of_joining and password and confirm_password):
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
            course=course,
            department=department,
            semester=semester,
            year_of_joining=year_of_joining,
            password=hashed_password,
            is_active=True  # Assuming user is active by default
        )
        student.save()

        messages.success(request, "Registration successful!")
        return redirect("login")  # Redirect to registration page (update URL name if needed)

    return render(request, "mainsite/registration.html")