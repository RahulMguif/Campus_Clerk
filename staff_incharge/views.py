from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from office_admin.models import *
from mainsite.models import *

# Create your views here.
def staff_incharge_home(request):
    return render(request,"staff_incharge/home.html")



def view_all_student(request):
    # Get the logged-in staff incharge's email from session
    staff_incharge_email = request.session.get('username')

    if not staff_incharge_email:
        messages.error(request, "You are not logged in. Please log in again.")
        return redirect('home')
    
    # Fetch the staff incharge object using the email
    staff_incharge_obj = staff_incharge.objects.filter(email=staff_incharge_email, delete_status=False).first()

    if not staff_incharge_obj:
        messages.error(request, "Invalid staff incharge account.")
        return redirect('home')

    # Get students where the department matches the staff incharge's department
    students = student_registration.objects.all().order_by('-id')
    events = event.objects.all().order_by('-id')

    return render(request,"staff_incharge/view_students.html", {'students': students, 'events':events,})


from django.http import JsonResponse

def assign_programme_coordinator(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        event_id = request.POST.get("event_id")
        staff_incharge_email = request.session.get('username')

        if not staff_incharge_email:
            return JsonResponse({"status": "error", "message": "You are not logged in"}, status=403)

        staff_incharge_obj = staff_incharge.objects.filter(email=staff_incharge_email, delete_status=False).first()

        if not staff_incharge_obj:
            return JsonResponse({"status": "error", "message": "Invalid staff incharge account"}, status=403)

        student = get_object_or_404(student_registration, id=student_id)

        # Get current coordinators for the same department & semester
        current_coordinators = student_registration.objects.filter(
            department=student.department,
            semester=student.semester,
            is_programme_coordinator=True
        ).order_by("date_joined")  # Order by oldest first

        removed_message = ""

        if current_coordinators.count() >= 2:
            # Remove the oldest coordinator
            oldest_coordinator = current_coordinators.first()
            removed_message = f"{oldest_coordinator.fullname} was removed as Programme Coordinator."
            oldest_coordinator.is_programme_coordinator = False
            oldest_coordinator.event_coordinated = None  # Reset event
            oldest_coordinator.save()

        # Assign the new student as a programme coordinator
        student.is_programme_coordinator = True

        # Update the event if provided
        if event_id:
            event_obj = get_object_or_404(event, id=event_id)
            student.event_coordinated = event_obj.event_name

        student.save()

        return JsonResponse({
            "status": "success",
            "message": f"{student.fullname} is now the Programme Coordinator for {student.event_coordinated}.",
            "removed_message": removed_message
        })

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)



from django.shortcuts import render, redirect
from django.contrib import messages
# from .models import staff_advisor, student_registration, departments, course
from staff_advisor.models import *
from mainsite.models import *

from django.contrib.auth.hashers import make_password  # To hash passwords

def incharge_add_student(request):
    if request.method == "POST":
        # Get logged-in staff incharge
        staff_incharge_email = request.session.get('username')

        if not staff_incharge_email:
            messages.error(request, "You are not logged in. Please log in again.")
            return redirect('home')

        staff_incharge_obj = staff_incharge.objects.filter(email=staff_incharge_email, delete_status=False).first()
        if not staff_incharge_obj:
            messages.error(request, "Invalid staff incharge account.")
            return redirect('home')

        # Get form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        course_id = request.POST.get('course')
        department_id = request.POST.get('department')
        year_of_joining = request.POST.get('year_of_joining')
        semester = request.POST.get('semester')

        # Check if student email already exists
        if student_registration.objects.filter(email=email).exists():
            messages.error(request, "A student with this email already exists.")
            return redirect('view_all_student')

        # Fetch course name
        course_obj = course.objects.filter(id=course_id).first()
        course_name = course_obj.course_name if course_obj else "Unknown"

        # Fetch department name
        department_obj = departments.objects.filter(id=department_id).first()
        department_name = department_obj.department_name if department_obj else "Unknown"

        # Create new student entry
        student = student_registration(
            fullname=full_name,
            email=email,
            password=make_password(password),  # Hash the password before storing
            mobile=mobile,
            course=course_name,
            department=department_name,
            semester=semester,
            year_of_joining=year_of_joining,
            is_active=True
        )
        student.save()

        messages.success(request, "Student added successfully!")
        return redirect('view_all_student')

    else:
        # Load department & courses for the form
        staff_incharge_email = request.session.get('username')
        staff_incharge_obj = staff_incharge.objects.filter(email=staff_incharge_email, delete_status=False).first()
        
        if not staff_incharge_obj:
            messages.error(request, "Invalid staff advisor account.")
            return redirect('home')

        # Fetch all departments and courses for dropdown
        departments_list = departments.objects.all()
        courses_list = course.objects.all()

        context = {
            'departments': departments_list,
            'courses': courses_list,
        }
        return render(request, "staff_incharge/add_students_coordinator.html", context)