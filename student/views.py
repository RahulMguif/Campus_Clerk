from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.files.storage import FileSystemStorage
import traceback
from django.contrib import messages
from campus_clerk import settings

from office_admin.models import *
from staff_incharge.models import notification

from .models import *
from datetime import datetime, date, timedelta
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from django.http import JsonResponse
from django.template.loader import render_to_string


# Create your views here.


def student_home(request):
    try:
        current_user = request.session.get('student_id')
        if current_user is None:
            return redirect('404')

        # Fetch the student details using the primary key
        student = student_registration.objects.filter(pk=current_user).first()
        application = student_application_request.objects.filter(student_pk=current_user, delete_status=0).count()
        approved_applications=student_application_request.objects.filter(student_pk=current_user,office_approval_status= 'Approved').count()
        print('approved_applications',approved_applications)
        print("application count:",application)
        
        if not student:
            return redirect('404')  # Redirect if student not found

        # Pass student data (fullname, email) to the template
        context = {
            'student_name': student.fullname,
            'student_email' : student.email,
            'profile_pic_url': student.profile_pic_url,  # Pass profile pic URL
            'application':application,
            'approved_applications':approved_applications
        }
        return render(request, 'student/home.html', context)

    except Exception as e:
        print('Exception in student_home:', e)
        traceback_str = traceback.format_exc()
        print('\ntraceback_str:', traceback_str)
        feed_exists = feedback_enable.objects.filter(enable_status=1).exists()  # Returns True if at least one exists
    context = {'feed': feed_exists}  # Now, feed is True or False
    return render(request, 'student/home.html', context)

    


def application_form(request):
    try:
        current_user = request.session.get('student_id')
        if current_user == None:
            return redirect('404')
        
        # Fetch the student details from session
        current_user_email = request.session.get('student_email')
        
        with transaction.atomic():
            today_date = date.today().strftime('%y%m%d')  # Format: YYMMDD
            
            # Get the last application number globally (not filtering by date)
            last_application = student_application_request.objects.order_by('-student_application_no').first()
            
            # Extract the last numeric part and increment
            if last_application:
                last_number = int(last_application.student_application_no[-2:])  # Extract last 2 digits
            else:
                last_number = 0  # Start from 01 if no previous applications exist

            application_number = f"AP{today_date}{last_number + 1:02d}"

        print('Application ID genarated it is, Application_number : ', application_number)

        if request.method == 'POST':
            full_name = request.POST.get('full_name')
            certificate_service = request.POST.get('certificate')
            gender = request.POST.get('gender')
            course_id = request.POST.get('course')  # Fetch course ID
            branch_id = request.POST.get('branch')  # Fetch department ID
            admission_no = request.POST.get('admission_no')
            date_of_admission = request.POST.get('admission_date')
            university_name = request.POST.get('university_name')
            university_reg_no = request.POST.get('university_reg_no')
            semester = request.POST.get('semester')
            hostel_name = request.POST.get('hostel_name')
            hostel_admission_date = request.POST.get('hostel_admission_date')
            tc_no = request.POST.get('tc_no')
            tc_date = request.POST.get('tc_date')
            address = request.POST.get('address')
            phone_number = request.POST.get('phone')
            student_email = request.POST.get('student_email')

            # Fetch course name from database
            try:
                course_obj = course.objects.get(id=course_id)
                student_course = course_obj.course_name
            except course.DoesNotExist:
                student_course = None

            # Fetch department (branch) name from database
            try:
                branch_obj = departments.objects.get(id=branch_id)
                branch = branch_obj.department_name
            except departments.DoesNotExist:
                branch = None

            application_date = timezone.now()

            # Convert to YYYY-MM-DD format
            if date_of_admission:
                date_of_admission = datetime.strptime(date_of_admission, "%Y-%m-%d").date()
            else:
                date_of_admission = None

            if hostel_admission_date:
                hostel_admission_date = datetime.strptime(hostel_admission_date, "%Y-%m-%d").date()
            else:
                hostel_admission_date = None

            if tc_date:
                tc_date = datetime.strptime(tc_date, "%Y-%m-%d").date()
            else:
                tc_date = None


            # Initialize the email validator
            validator = EmailValidator()

            # Validate personal_email
            try:
                validator(student_email)
                print(f"Email '{student_email}' is valid.")  # Confirm valid email
            except ValidationError:
                print(f"Email '{student_email}' is invalid.")  # Print email error
                messages.error(request, 'Enter a valid personal email address.')
                return redirect('registration')

            # =====File Uploads=====

            # Handle signature upload (Mandatory)

            signature_file = None  # Initialize
            attached_sign_url = None

            if 'student_sign' in request.FILES:
                signature_file = request.FILES['student_sign']
                fs = FileSystemStorage(location='media/attached_signature')
                attached_sign = fs.save(signature_file.name, signature_file)
                attached_sign_url = fs.base_location + '/' + attached_sign
            else:
                messages.error(request, "Signature is mandatory. Please upload a signature file.")
                return redirect('registration')

            # Handle proof document (Optional)

            document_file = None  # Initialize the variable to avoid UnboundLocalError
            attached_proof_url = None  # Default to None

            if 'reason_document' in request.FILES:
                document_file = request.FILES['reason_document']
                fs = FileSystemStorage(location='media/attached_proofs')
                attached_proof = fs.save(document_file.name, document_file)
                attached_proof_url = fs.base_location + '/' + attached_proof
            else:
                attached_proof_url = None  # No proof uploaded

            
            print('=========================CERTIFICATE DETAILS=========================')
            print('Attached Proof file', document_file)
            print('Attached Proof URL', attached_proof_url)

            print('Attached signature file', signature_file)
            print('Attached signature URL', attached_sign_url)

            # Fetch the student instance based on session ID
            try:
                student_instance = student_registration.objects.get(id=current_user)
            except student_registration.DoesNotExist:
                messages.error(request, "Invalid student ID. Please log in again.")
                return redirect('login')  # Redirect to login page if student is not found

            # Save the application request
            new_application_request = student_application_request.objects.create(student_pk = student_instance,
                                                                                 student_application_no = application_number,
                                                                                 full_name = full_name,
                                                                                 gender = gender,
                                                                                 course = student_course,
                                                                                 branch = branch,
                                                                                 admission_no = admission_no,
                                                                                 admission_date = date_of_admission,
                                                                                 university = university_name,
                                                                                 university_reg_no = university_reg_no,
                                                                                 semester = semester,
                                                                                 hostel_name = hostel_name,
                                                                                 hostel_admission_date = hostel_admission_date,
                                                                                 tc_no = tc_no,
                                                                                 tc_date = tc_date,
                                                                                 apply_for = certificate_service,
                                                                                 reason = attached_proof_url,
                                                                                 contact_address = address,
                                                                                 phone_number = phone_number,
                                                                                 student_signature_url = attached_sign_url,
                                                                                 student_email_address = student_email,
                                                                                 application_status = 'Initial',
                                                                                 application_submitted_date = application_date,
                                                                                 )
            print('registration POST Success')
            messages.success(request,
                             f'Your Application Submit Successfully.You will get a response within 48hr after review your application..')

            # contexts = {'username': user_nme, 'useremail': user_email}
            # return render(request, 'user_admin/registration.html', contexts)
            # return render(request, 'student/student_application_form.html', {'application_number': application_number})
            return redirect('my_applications')
        else:
            print('registration ELSE')

            # Fetch courses and departments
            courses = course.objects.filter(delete_status=False)
            departments_list = departments.objects.filter(delete_status=False)

            contexts = {
                'student_email': current_user_email, 
                'application_number': application_number,
                'courses': courses,
                'departments': departments_list,
                }
            # return render(request, 'user_admin/registration.html', contexts)
            return render(request, 'student/student_application_form.html', contexts)


    except Exception as e:
        print('Exception registration', e)
        traceback_str = traceback.format_exc()
        print('\ntraceback_str', traceback_str)
        # contexts = {'username': user_nme, 'useremail': user_email}
        # return render(request, 'user_admin/registration.html', contexts)
        return render(request, 'student/student_application_form.html', {'application_number': application_number})
    

def my_applications(request):
    try:
        # Get the currently logged-in student's ID from session
        current_user_id = request.session.get('student_id')

        if current_user_id is None:
            return redirect('404')
        
        current_user_email = request.session.get('student_email')

        # Fetch applications for the current student
        applications = student_application_request.objects.filter(
            student_pk_id=current_user_id, 
            delete_status=False  # Exclude deleted applications
        ).order_by('-id')  # Order by latest submitted

    except Exception as e:
        print('Exception in my_applications:', e)
        traceback_str = traceback.format_exc()
        print('\ntraceback_str:', traceback_str)
        return render(request, 'student/view_applications.html', {'applications': []})

    return render(request, 'student/view_applications.html', {'applications': applications, 'student_email':current_user_email})


from django.utils import timezone

def add_feedback(request):
    if request.method=='POST':
        depart=request.POST.get('department')
        department_obj=departments.objects.get(id=depart)
        # return HttpResponse(depart)
        semester=request.POST.get('semester')
        comment=request.POST.get('comment')
        feedback_for = request.POST.get('feedback_for')
        feed=feedback()
        feed.department_pk=department_obj
        feed.semester=semester
        feed.comment=comment
        feed.feedback_for = feedback_for
        feed.is_flaged=0
        feed.submitted_date=timezone.now()
        feed.delete_status=0
        feed.save()
        print("feedback saved")
        messages.success(request, 'Successfully submitted the feedback')
        return redirect('add_feedback')
    student_id=request.session["student_id"]
    department=departments.objects.filter(delete_status=0)
    context={'department':department,'student_id':student_id}
    return render(request,"student/feedback.html",context)

    
def feedback_view(request):
    student_id = request.session.get("student_id")
    student=student_registration.objects.get(id=student_id)
    stud_dept=student.department
    stud_sem=student.semester

    # Fetch the department ID based on the department name
    try:
        department = departments.objects.get(department_name=stud_dept)
        department_id = department.id
    except departments.DoesNotExist:
        # Handle the case if the department does not exist
        department_id = None

    # return HttpResponse(stud_dept)
    feed = feedback.objects.filter(delete_status=0, department_pk_id__department_name=stud_dept,is_flaged=0,semester=stud_sem)
    feeds_app = feedback.objects.filter(delete_status=0, department_pk=department_id,is_flaged=1)
    context={'feed':feed, 'feeds_app':feeds_app}
    return render(request,"student/feedback_view.html",context)



# def flag_comment(request):
#     if request.method=='POST':
#         id=request.POST.get('flaged')
#         flag=feedback.objects.get(id=id)
#         flag.is_flaged=1
#         flag.save()
#         messages.success(request, 'Successfully flaged the comment')
#         return redirect('feedback_view')


def flag_comment(request):
    if request.method == 'POST':
        id = request.POST.get('flaged')
        reason = request.POST.get('flag_reason')  # Get the flag reason

        try:
            flag = feedback.objects.get(id=id)
            flag.is_flaged = True
            flag.flag_reason = reason  # Save the reason in the database
            flag.save()
            messages.success(request, 'Successfully flagged the comment with reason.')
        except feedback.DoesNotExist:
            messages.error(request, 'Feedback not found.')

        return redirect('feedback_view')

    

def edit_profile(request):
    try:
        current_user = request.session.get('student_id')
        if current_user is None:
            return redirect('404')
        
        # Fetch the student details from session
        current_user_email = request.session.get('student_email')

        student = student_registration.objects.filter(pk=current_user).first()
        if not student:
            return redirect('404')

        if request.method == 'POST':
            student.fullname = request.POST.get('fullname')
            student.email = request.POST.get('email')
            student.mobile = request.POST.get('mobile')
            student.course = request.POST.get('course')
            student.department = request.POST.get('department')
            student.semester = request.POST.get('semester')
            student.year_of_joining = request.POST.get('year_of_joining')
            
            # Handle Profile Picture Upload
            if 'profile_pic' in request.FILES:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage(location='media/profile_pic')  # Save in 'media/profile_pic' folder
                filename = fs.save(profile_pic.name, profile_pic)
                student.profile_pic_url = 'profile_pic/' + filename  # Save relative path in DB

            student.save()
            messages.success(request, "Your profile has been updated successfully")
            return redirect('student_dashboard')

        context = {
            'student': student,
            'courses': course.objects.all(),
            'departments': departments.objects.all(),
            'student_email': current_user_email,
        }
        return render(request, 'student/edit_profile.html', context)
    except Exception as e:
        print('Exception in edit_profile:', e)
        traceback_str = traceback.format_exc()
        print('\ntraceback_str:', traceback_str)
        return render(request, 'student/edit_profile.html')

    




# def view_documents(request):
#     if request.method == "POST":
#         document_name = request.POST.get("document_name")
#         reason = request.POST.get("description")

#         # Get student ID from session
#         student_id = request.session.get("student_id")  
        
#         if not student_id:
#             messages.error(request, "Student not logged in!")
#             return redirect("view_documents")

#         try:
#             student = student_registration.objects.get(pk=student_id)
#         except student_registration.DoesNotExist:
#             messages.error(request, "Invalid student ID!")
#             return redirect("view_documents")

#         # Save document with associated student
#         new_document = office_documents(
#             document_name=document_name,
#             reason=reason,
#             student_pk=student
#         )
#         new_document.save()

#         messages.success(request, "Document saved successfully!")
#         return redirect("view_documents")  # Redirect after save

#     all_documents = office_documents.objects.all()
#     return render(request, "student/view_documents.html", {"all_documents": all_documents})


def view_documents(request):
    if request.method == "POST":
        document_name = request.POST.get("document_name")
        reason = request.POST.get("description")

        # Get student ID from session
        student_id = request.session.get("student_id")  
        
        if not student_id:
            messages.error(request, "Student not logged in!")
            return redirect("view_documents")

        try:
            student = student_registration.objects.get(pk=student_id)
        except student_registration.DoesNotExist:
            messages.error(request, "Invalid student ID!")
            return redirect("view_documents")

        # Save document with associated student
        office_documents.objects.create(
            document_name=document_name,
            reason=reason,
            student_pk=student
        )
        messages.success(request, "Document requested successfully!")
        return redirect("view_documents")

    # Filter documents only for the logged-in student
    student_id = request.session.get("student_id")
    all_documents = office_documents.objects.filter(student_pk_id=student_id)

    return render(request, "student/view_documents.html", {"all_documents": all_documents})



def notification_view(request):
    try:
        current_user = request.session.get('student_id')
        if current_user is None:
            return redirect('404')
        note=notification.objects.filter(delete_status=0).order_by('-id')
        context={'note':note}
        return render(request,'student/notification_view.html',context)
    except Exception as e:
        print('Exception in edit_profile:', e)
        traceback_str = traceback.format_exc()
        print('\ntraceback_str:', traceback_str)
        return render(request, 'student/edit_profile.html')


def add_announcement(request):
    if request.method == "POST":
        heading = request.POST.get('name')
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
        messages.success(request, 'Successfully added the announcement')
        return redirect("add_announcement") 
    all_notification=notification.objects.filter(delete_status=0)
    context={'all_notification':all_notification}
    return render(request,"student/add_announcement.html",context)        

from django.shortcuts import get_object_or_404, redirect


def delete_announcement(request, announcement_id):
    if request.method == "POST":
        announcement = get_object_or_404(notification, id=announcement_id)
        announcement.delete()
        messages.success(request, "Announcement deleted successfully.")
        return redirect('add_announcement')  # Change to the name of your announcement list view
    return redirect('add_announcement')



def add_attendance(request):
    if request.method == "POST":
        event_id = request.POST.get('name')  # Get selected event's ID
        attendance_sheet = request.FILES.get('attendance_sheet')

        if not event_id or not attendance_sheet:
            messages.error(request, "Please select an event and upload a file.")
            return redirect('add_attendance')

        try:
            event = notification.objects.get(id=event_id)  # Get event by ID

            # Save the uploaded file
            fs = FileSystemStorage(location=settings.MEDIA_ROOT + '/attendance_sheets')
            file_name = fs.save(attendance_sheet.name, attendance_sheet)
            file_url = 'media/attendance_sheets/' + file_name  # Store relative URL

            # Update the notification with attendance URL
            event.attendance_url = file_url
            event.save()

            messages.success(request, "Attendance sheet uploaded successfully.")
            return redirect('add_attendance')
        
        except notification.DoesNotExist:
            messages.error(request, "Selected event does not exist.")
            return redirect('add_attendance')

    # Fetch events for the dropdown
    events = notification.objects.filter(delete_status=0)
    all_events = notification.objects.filter(delete_status=0).exclude(attendance_url__isnull=True).exclude(attendance_url="")

    return render(request, "student/add_attendance.html", {'all_events': all_events,'events':events})



def apply_notification(request, pk):
    try:
        current_user = request.session.get('student_id')
        if current_user is None:
            return redirect('notification_view')

        # Retrieve the specific notification using the ID
        note = get_object_or_404(notification, id=pk)

        course_obj = course.objects.all()
        department_obj = departments.objects.all()

        # Render the application form with the notification details
        context = {'note': note,
                   'courses': course_obj,
                   'departments': department_obj,
                   }
        return render(request, 'student/apply_notification.html', context)

    except Exception as e:
        print(f'Error in apply_notification: {e}')
        return redirect('notification_view')
    

def submit_application(request):
    if request.method == 'POST':
        try:
            notification_id = request.POST.get('notification_id')
            full_name = request.POST.get('full_name')
            email_address = request.POST.get('email_address')
            course_id = request.POST.get('course_pk')
            department_id = request.POST.get('department_pk')
            semester = request.POST.get('semester')
            mobile_number = request.POST.get('mobile_number')

            # Validate notification existence
            notification_obj = notification.objects.get(pk=notification_id)

            # Validate course and department existence
            course_obj = course.objects.get(pk=course_id)
            department_obj = departments.objects.get(pk=department_id)

            # Insert the data into the event_registration model
            event_registration.objects.create(
                notification_pk=notification_obj,
                full_name=full_name,
                email_address=email_address,
                course_pk=course_obj,
                department_pk=department_obj,
                semester=semester,
                mobile_number=mobile_number,
                submitted_date=timezone.now()
            )

            messages.success(request, "Application submitted successfully.")
            return redirect('notification_view')  # Redirect to a success page or desired URL

        except notification.DoesNotExist:
            messages.error(request, "Notification not found.")
        except course.DoesNotExist:
            messages.error(request, "Course not found.")
        except departments.DoesNotExist:
            messages.error(request, "Department not found.")
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, "An error occurred while submitting the application.")
            
    return redirect('notification_view')  # Redirect to an error page or back to form on failure