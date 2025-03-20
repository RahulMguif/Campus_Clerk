from django.shortcuts import render, redirect, get_object_or_404
from staff_advisor.models import *
from django.contrib import messages
from student.models import *
from django.core.files.storage import FileSystemStorage

# Create your views here.
# def staff_home(request):
#     return render(request,"staff_advisor/home.html")

def staff_home(request):
    # Get the logged-in staff advisor's email from session
    staff_email = request.session.get('username')  

    if not staff_email:
        messages.error(request, "You are not logged in. Please log in again.")
        return redirect('home')

    # Fetch the staff advisor object using the email
    staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()

    if not staff_advisor_obj:
        messages.error(request, "Invalid staff advisor account.")
        return redirect('home')

    # Pass the staff advisor name and email to the template
    return render(request, "staff_advisor/home.html", {
        "staff_name": staff_advisor_obj.name,
        "staff_email": staff_advisor_obj.email
    })


def view_student_applications(request):
    # Get the logged-in staff advisor's email from session
    staff_email = request.session.get('username')  

    if not staff_email:
        messages.error(request, "You are not logged in. Please log in again.")
        return redirect('home')

    # Fetch the staff advisor object using the email
    staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()

    if not staff_advisor_obj:
        messages.error(request, "Invalid staff advisor account.")
        return redirect('home')

    # Get applications where the department matches the staff advisor's department
    application_details = student_application_request.objects.filter(branch=staff_advisor_obj.department_pk.department_name).order_by('-id')

    return render(request, 'staff_advisor/view_student_applications.html', {'application_details': application_details, 'staff_email': staff_advisor_obj.email})




from django.shortcuts import get_object_or_404
from django.contrib import messages
from student.models import student_application_request
from staff_advisor.models import staff_advisor  # Import the required models

def update_staff_remark(request, application_id):
    # Get the logged-in staff advisor's email from session
    email = request.session.get('username')

    if not email:
        messages.error(request, "Session expired or user not logged in.")
        return redirect('home')  # Redirect to login page or appropriate page

    # Fetch the staff advisor object using email
    staff_advisor_instance = get_object_or_404(staff_advisor, email=email)

    application_entry = get_object_or_404(student_application_request, id=application_id)

    if request.method == 'POST':
        # staff_advisor_remark = request.POST.get('staff_advisor_remark', '')
        staff_advisor_signature = request.FILES.get('staff_advisor_signature')

        # Update the application with the logged-in staff advisor's details
        application_entry.staff_advisor_pk = staff_advisor_instance
        # application_entry.staff_advisor_remark = staff_advisor_remark

        # Handle signature file upload
        if staff_advisor_signature:
            fs = FileSystemStorage(location='media/staff_signatures/')
            filename = fs.save(staff_advisor_signature.name, staff_advisor_signature)
            application_entry.staff_advisor_signature_url = f'media/staff_signatures/{filename}'

        application_entry.save()
        messages.success(request, "Application updated successfully!")
        return redirect('view_student_applications')  # Adjust based on your URL name

    return render(request, 'staff_advisor/update_staff_remark.html', {'application_entry': application_entry})

from django.utils.timezone import now



def approval_status_staff_advisor(request, application_id):
    # Get the logged-in staff advisor's email from session
    email = request.session.get('username')

    if not email:
        messages.error(request, "Session expired or user not logged in.")
        return redirect('home')  # Redirect to login page

    # Fetch the staff advisor object using email
    staff_advisor_instance = get_object_or_404(staff_advisor, email=email)

    # Get the application
    application = get_object_or_404(student_application_request, pk=application_id)

    if request.method == "POST":
        new_status = request.POST.get("staff_advisor_status")  # Get status from form
        remark = request.POST.get("staff_advisor_remark", "").strip()  # Get remarks

        # Update application with staff advisor details
        application.staff_advisor_pk = staff_advisor_instance
        application.staff_approval_status = new_status
        application.staff_advisor_remark = remark  # Save remark
        application.staff_approval_date = now()
        application.save()

        messages.success(request, "Application status updated successfully.")
        return redirect("view_student_applications")  # Redirect to applications page

    messages.error(request, "Invalid request.")
    return redirect("view_student_applications")



def view_students_by_department(request):
    # Get the logged-in staff advisor's email from session
    staff_email = request.session.get('username')

    if not staff_email:
        messages.error(request, "You are not logged in. Please log in again.")
        return redirect('home')

    # Fetch the staff advisor object using the email
    staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()

    if not staff_advisor_obj:
        messages.error(request, "Invalid staff advisor account.")
        return redirect('home')

    # Get students where the department matches the staff advisor's department
    students = student_registration.objects.filter(department=staff_advisor_obj.department_pk.department_name, is_approved='1')

    return render(request, 'staff_advisor/view_students.html', {'students': students, 'staff_email': staff_advisor_obj.email})

from django.http import JsonResponse

def assign_class_rep(request):
    if request.method == "POST":
        student_ids = request.POST.get("student_ids", "").strip()  
        staff_email = request.session.get('username')

        if not staff_email:
            return JsonResponse({"status": "error", "message": "You are not logged in"}, status=403)

        staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()
        if not staff_advisor_obj:
            return JsonResponse({"status": "error", "message": "Invalid staff advisor account"}, status=403)

        student_ids = [sid.strip() for sid in student_ids.split(",") if sid.strip().isdigit()]  

        if not student_ids:
            return JsonResponse({"status": "error", "message": "No valid student IDs provided"}, status=400)

        # Fetch first student to get department and semester
        first_student = get_object_or_404(student_registration, id=student_ids[0])
        department = first_student.department
        semester = first_student.semester

        if len(student_ids) > 2:
            return JsonResponse({"status": "error", "message": "Only 2 class representatives allowed per semester."})

        # Reset all students in the same department and semester
        student_registration.objects.filter(department=department, semester=semester).update(is_class_rep=False)

        # Assign selected students as class reps (limit to 2)
        updated_students = student_registration.objects.filter(id__in=student_ids[:2])
        updated_students.update(is_class_rep=True)

        student_names = " and ".join([student.fullname for student in updated_students])

        return JsonResponse({"status": "success", "message": f"{student_names} have been selected as class representatives."})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)



from django.shortcuts import render, redirect
from django.contrib import messages
# from .models import staff_advisor, student_registration, departments, course
from staff_advisor.models import *
from mainsite.models import *

from django.contrib.auth.hashers import make_password  # To hash passwords

def add_student(request):
    if request.method == "POST":
        # Get logged-in staff advisor
        staff_email = request.session.get('username')

        if not staff_email:
            messages.error(request, "You are not logged in. Please log in again.")
            return redirect('home')

        staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()
        if not staff_advisor_obj:
            messages.error(request, "Invalid staff advisor account.")
            return redirect('home')

        # Get form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        course_id = request.POST.get('course')  # Course is selected from dropdown
        year_of_joining = request.POST.get('year_of_joining')
        semester = request.POST.get('semester')

        # Check if student email already exists
        if student_registration.objects.filter(email=email).exists():
            messages.error(request, "A student with this email already exists.")
            return redirect('view_students_by_department')

        # Fetch department based on staff advisor
        department_name = staff_advisor_obj.department_pk.department_name
        course_obj = course.objects.filter(id=course_id).first()

        # Create new student entry
        student = student_registration(
            fullname=full_name,
            email=email,
            password=make_password(password),  # Hash the password before storing
            mobile=mobile,
            course=course_obj.course_name if course_obj else "Unknown",  # Ensure valid course
            department=department_name,
            semester=semester,  # Default semester (Modify based on input)
            year_of_joining=year_of_joining,  # Modify as needed
            is_active=True
        )
        student.save()

        messages.success(request, "Student added successfully!")
        return redirect('approve_reg_student')

    else:
        # Load department & courses for the form
        staff_email = request.session.get('username')
        staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()
        
        if not staff_advisor_obj:
            messages.error(request, "Invalid staff advisor account.")
            return redirect('home')

        department = staff_advisor_obj.department_pk
        courses = course.objects.all()  # Get all courses

        return render(request, 'staff_advisor/add_students.html', {'department': department, 'courses': courses})



def view_feedback(request):
    email=request.session.get('username')
    staff=staff_advisor.objects.get(email=email)
    staff_dept=staff.department_pk
    feed = feedback.objects.filter(delete_status=0, department_pk=staff_dept,is_flaged=0)
    feeds_app = feedback.objects.filter(delete_status=0, department_pk=staff_dept,is_flaged=1)
    context={'feed':feed,'feeds_app':feeds_app}
    return render(request,"staff_advisor/feedback_view.html",context)

def approve_reg_student(request):
    staff_email = request.session.get('username')

    if not staff_email:
        messages.error(request, "You are not logged in. Please log in again.")
        return redirect('home')

    # Fetch the staff advisor object using the email
    staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()

    if not staff_advisor_obj:
        messages.error(request, "Invalid staff advisor account.")
        return redirect('home')

    registered_student=student_registration.objects.filter(department=staff_advisor_obj.department_pk.department_name)
    contexs={'registered_student':registered_student}
   
    return render(request,'staff_advisor/approve_reg_students.html',contexs)



def registration_status(request,student_pk):
    if request.method == "POST":
        students = get_object_or_404(student_registration, pk=student_pk)
        new_status = request.POST.get("adminstatus")  # Get status from form

        # Update application status and date
        students.is_approved = new_status
        students.save()

        messages.success(request, "status updated successfully.")
        return redirect(approve_reg_student)
    
    messages.error(request, "Invalid request.")
    return render(request,'staff_advisor/approve_reg_students.html')

from datetime import datetime, timedelta
from django.utils.timezone import make_aware

def event_participants(request):
    student = student_registration.objects.all()
    participant = event_registration.objects.all()

    # Get filter values
    name = request.GET.get("name", "").strip()
    from_date = request.GET.get("from_date", "")
    to_date = request.GET.get("to_date", "")

    # Apply name filter
    if name:
        participant = participant.filter(full_name__icontains=name)

    # Handle date filters correctly
    if from_date:
        from_date = datetime.strptime(from_date, "%Y-%m-%d")  # Convert string to date
        from_date = make_aware(from_date)  # Ensure it's timezone aware
        participant = participant.filter(submitted_date__gte=from_date)

    if to_date:
        to_date = datetime.strptime(to_date, "%Y-%m-%d")  # Convert string to date
        to_date = make_aware(to_date + timedelta(days=1)) - timedelta(seconds=1)  # Include full day
        participant = participant.filter(submitted_date__lte=to_date)

    context = {"participant": participant, "student": student}
    return render(request, "staff_advisor/event_participants.html", context)