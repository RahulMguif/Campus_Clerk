from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from campus_clerk import settings
from office_admin.models import *
from mainsite.models import *
from staff_incharge.models import notification
from student.models import event_registration

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

# def assign_programme_coordinator(request):
#     if request.method == "POST":
#         student_id = request.POST.get("student_id")
#         event_id = request.POST.get("event_id")
#         staff_incharge_email = request.session.get('username')

#         if not staff_incharge_email:
#             return JsonResponse({"status": "error", "message": "You are not logged in"}, status=403)

#         staff_incharge_obj = staff_incharge.objects.filter(email=staff_incharge_email, delete_status=False).first()

#         if not staff_incharge_obj:
#             return JsonResponse({"status": "error", "message": "Invalid staff incharge account"}, status=403)

#         student = get_object_or_404(student_registration, id=student_id)

#         # Get current coordinators for the same department & semester
#         current_coordinators = student_registration.objects.filter(
#             department=student.department,
#             semester=student.semester,
#             is_club_coordinator=True
#         ).order_by("date_joined")  # Order by oldest first

#         removed_message = ""

#         if current_coordinators.count() >= 2:
#             # Remove the oldest coordinator
#             oldest_coordinator = current_coordinators.first()
#             removed_message = f"{oldest_coordinator.fullname} was removed as Programme Coordinator."
#             oldest_coordinator.is_club_coordinator = False
#             oldest_coordinator.event_coordinated = None  # Reset event
#             oldest_coordinator.save()

#             removed_student = student_registration.objects.get(id=oldest_coordinator.id)
#             print(removed_student.is_club_coordinator)  # Should print False


#         # Assign the new student as a programme coordinator
#         student.is_club_coordinator = True

#         # Update the event if provided
#         if event_id:
#             event_obj = get_object_or_404(event, id=event_id)
#             student.event_coordinated = event_obj.event_name

#         student.save()

#         return JsonResponse({
#             "status": "success",
#             "message": f"{student.fullname} is now the Programme Coordinator for {student.event_coordinated}.",
#             "removed_message": removed_message
#         })

#     return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def assign_programme_coordinator(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        event_id = request.POST.get("event_id")
        staff_incharge_email = request.session.get('username')

        if not staff_incharge_email:
            return JsonResponse({"status": "error", "message": "You are not logged in"}, status=403)

        # Fetch staff incharge details
        staff_incharge_obj = staff_incharge.objects.filter(email=staff_incharge_email, delete_status=False).first()

        if not staff_incharge_obj:
            return JsonResponse({"status": "error", "message": "Invalid staff incharge account"}, status=403)

        # Get the student
        student = get_object_or_404(student_registration, id=student_id)

        # Get current coordinators in the same department & semester
        current_coordinators = student_registration.objects.filter(
            department=student.department,
            semester=student.semester,
            is_club_coordinator=True
        ).order_by("date_joined")  # Order by oldest first

        removed_message = ""
        removed_student_id = None

        if current_coordinators.count() >= 2:
            # Remove the oldest coordinator
            oldest_coordinator = current_coordinators.first()
            removed_message = f"{oldest_coordinator.fullname} was removed as Programme Coordinator."
            removed_student_id = oldest_coordinator.id  # Capture removed student's ID
            oldest_coordinator.is_club_coordinator = False
            oldest_coordinator.event_coordinated = None  # Reset event
            oldest_coordinator.save(update_fields=['is_club_coordinator', 'event_coordinated'])  # ✅ Explicit save

        # Assign the new student as a Programme Coordinator
        student.is_club_coordinator = True

        # Update the event if provided
        if event_id:
            event_obj = get_object_or_404(event, id=event_id)
            student.event_coordinated = event_obj.event_name

        student.save(update_fields=['is_club_coordinator', 'event_coordinated'])  # ✅ Explicit save

        return JsonResponse({
            "status": "success",
            "message": f"{student.fullname} is now the Programme Coordinator for {student.event_coordinated}.",
            "removed_message": removed_message,
            "removed_student_id": removed_student_id  # Send removed student ID for UI update
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
        event_id = request.POST.get('events')  # Fetch selected event

        # Check if student email already exists
        if student_registration.objects.filter(email=email).exists():
            messages.error(request, "A student with this email already exists.")
            return redirect('view_all_student')

        # Fetch course and department names
        course_obj = get_object_or_404(course, id=course_id)
        department_obj = get_object_or_404(departments, id=department_id)

        # Fetch event
        event_obj = get_object_or_404(event, id=event_id)

        # Check if there are already 2 coordinators in this department & semester
        current_coordinators = student_registration.objects.filter(
            department=department_obj.department_name,
            semester=semester,
            is_club_coordinator=True
        ).order_by("date_joined")  # Oldest first

        removed_message = ""

        if current_coordinators.count() >= 2:
            # Remove the oldest coordinator
            oldest_coordinator = current_coordinators.first()
            removed_message = f"{oldest_coordinator.fullname} was removed as Programme Coordinator."
            oldest_coordinator.is_club_coordinator = False
            oldest_coordinator.event_coordinated = None  # Reset event
            oldest_coordinator.save()

        # Create new student entry
        student = student_registration(
            fullname=full_name,
            email=email,
            password=make_password(password),  # Hash the password
            mobile=mobile,
            course=course_obj.course_name,
            department=department_obj.department_name,
            semester=semester,
            year_of_joining=year_of_joining,
            is_active=True,
            is_club_coordinator=True,  # Assign as club coordinator
            event_coordinated=event_obj.event_name,  # Assign event
        )
        student.save()

        messages.success(request, f"{student.fullname} is now the Programme Coordinator for {student.event_coordinated}.")
        
        if removed_message:
            messages.warning(request, removed_message)  # Show removal message if applicable

        return redirect('view_all_student')

    else:
        # Load department & courses for the form
        staff_incharge_email = request.session.get('username')
        staff_incharge_obj = staff_incharge.objects.filter(email=staff_incharge_email, delete_status=False).first()
        
        if not staff_incharge_obj:
            messages.error(request, "Invalid staff advisor account.")
            return redirect('home')

        # Fetch all departments, courses, and events for dropdown
        departments_list = departments.objects.all()
        courses_list = course.objects.all()
        event_list = event.objects.all()

        context = {
            'departments': departments_list,
            'courses': courses_list,
            'event_list': event_list,
        }
        return render(request, "staff_incharge/add_students_coordinator.html", context)
    
    
    
from django.core.files.storage import FileSystemStorage

def add_notification(request):
    if request.method == "POST":
        heading = request.POST.get('heading')
        description = request.POST.get('description')
        date=request.POST.get('date')
        attached_sign_url = None  # Default to None
        if 'document' in request.FILES:
            signature_file = request.FILES['document']
            fs = FileSystemStorage(location=settings.MEDIA_ROOT + '/notification')
            attached_sign = fs.save(signature_file.name, signature_file)
            attached_sign_url = 'media/notification/' + attached_sign  # Store relative path
        # Create and save the notification
        notification.objects.create(
            heading=heading,
            description=description,
            document=attached_sign_url,
            delete_status='0',
            date=date
        )
        messages.success(request, 'Successfully added the notification')
        return redirect('add_notification')
    notif=notification.objects.filter(delete_status=0)
    context={'notification':notif}
    return render(request, "staff_incharge/add_notification.html",context)



def notification_delete(request):
    if request.method=="POST":
        id=request.POST.get('delete_id')
        delete=notification.objects.get(id=id)
        delete.delete_status=1
        delete.save()
        messages.success(request, 'Successfully deleted the notification')
        return redirect('add_notification')
    

# def event_participants(request):
#     # Get the logged-in staff incharge's email from session
#     staff_incharge_email = request.session.get('username')

#     if not staff_incharge_email:
#         messages.error(request, "You are not logged in. Please log in again.")
#         return redirect('home')
    
#     # Fetch the staff incharge object using the email
#     staff_incharge_obj = staff_incharge.objects.filter(email=staff_incharge_email, delete_status=False).first()

#     if not staff_incharge_obj:
#         messages.error(request, "Invalid staff incharge account.")
#         return redirect('home')
    
#     students = event_registration.objects.all().order_by('-id')
#     context = {
#         'students': students,
#     }
#     return render(request,"staff_incharge/event_participants.html", context)



def event_participants(request):
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

    # Get all notifications for dropdown
    notifications = notification.objects.filter(delete_status='0').order_by('-date')

    # Get all departments for dropdown
    departments_list = departments.objects.filter(delete_status='0')

    # Get all courses for dropdown
    course_list = course.objects.filter(delete_status='0')

    # Filtering by notification_pk
    notification_pk = request.GET.get('notification_pk')

    attendance_url = None
    if notification_pk:
        students = event_registration.objects.filter(notification_pk_id=notification_pk).order_by('-id')
        selected_notification = notification.objects.filter(id=notification_pk).first()
        
        # Get the attendance URL if available
        if selected_notification and selected_notification.attendance_url:
            attendance_url = selected_notification.attendance_url
    else:
        students = event_registration.objects.all().order_by('-id')

    context = {
        'students': students,
        'notifications': notifications,
        'selected_notification': notification_pk,
        'attendance_url': attendance_url,
        'departments': departments_list,
        'courses': course_list,
    }
    return render(request, "staff_incharge/event_participants.html", context)


from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib import messages

def add_student_to_event(request):
    if request.method == "POST":
        # Get the form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email_address')
        mobile = request.POST.get('mobile_number')
        course_id = request.POST.get('course_pk')
        department_id = request.POST.get('department_pk')
        semester = request.POST.get('semester')
        notification_id = request.GET.get('notification_pk')  # Get from query string

        # Validate that notification ID is present
        if not notification_id:
            messages.error(request, "No event selected.")
            return redirect('event_participants')  # Replace with your actual event list page

        # Get related objects
        try:
            notification_obj = notification.objects.get(pk=notification_id)
            course_obj = course.objects.get(pk=course_id)
            department_obj = departments.objects.get(pk=department_id)
        except (notification.DoesNotExist, course.DoesNotExist, departments.DoesNotExist):
            messages.error(request, "Invalid selection.")
            return redirect('event_participants')

        # Create and save the new event registration
        event_registration.objects.create(
            notification_pk=notification_obj,
            full_name=full_name,
            email_address=email,
            mobile_number=mobile,
            course_pk=course_obj,
            department_pk=department_obj,
            semester=semester,
            submitted_date=now()
        )

        messages.success(request, "Student added successfully.")
        return redirect('event_participants')  # Redirect back to the event page

    else:
        messages.error(request, "Invalid request method.")
        return redirect('event_participants')
