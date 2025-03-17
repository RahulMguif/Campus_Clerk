from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.files.storage import FileSystemStorage
import traceback
from django.contrib import messages

from office_admin.models import *

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
    student = student_registration.objects.get(id=student_id)
    stud_dept = student.department
    stud_sem = student.semester

    # Get Department ID
    try:
        department = departments.objects.get(department_name=stud_dept)
        department_id = department.id
    except departments.DoesNotExist:
        department_id = None

    # Capture Filters
    feedback_for = request.GET.get('feedback_for', 'Academics')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Filter Regular Feedback
    feed = feedback.objects.filter(
        delete_status=0,
        department_pk_id=department_id,
        semester=stud_sem,
        feedback_for=feedback_for,
        is_flaged=0
    )

    # Filter Flagged Feedback
    feeds_app = feedback.objects.filter(
        delete_status=0,
        department_pk_id=department_id,
        feedback_for=feedback_for,
        is_flaged=1
    )

    # Apply Date Filter if Provided
    if start_date and end_date:
        feed = feed.filter(submitted_date__range=[start_date, end_date])
        feeds_app = feeds_app.filter(submitted_date__range=[start_date, end_date])

    # Handle AJAX Request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        feedback_html = render_to_string('student/partials/feedback_table.html', {'feed': feed})
        flagged_html = render_to_string('student/partials/flagged_feedback_table.html', {'feeds_app': feeds_app})
        return JsonResponse({'feedback_html': feedback_html, 'flagged_html': flagged_html})

    # Render Full Page
    context = {'feed': feed, 'feeds_app': feeds_app}
    return render(request, "student/feedback_view.html", context)


from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404

from django.contrib.messages import get_messages

def flag_comment(request):
    if request.method == 'POST':
        id = request.POST.get('flaged')
        flag_reason = request.POST.get('flag_reason')

        if not id or not flag_reason:
            return JsonResponse({'error': 'Missing data'}, status=400)

        flag = get_object_or_404(feedback, id=id)
        flag.is_flaged = 1
        flag.flag_reason = flag_reason
        flag.save()
        messages.success(request, 'Successfully flagged the comment.')

        # ✅ Get messages
        storage = get_messages(request)
        success_message = ''
        for message in storage:
            success_message = str(message)

        # ✅ Refresh Tables
        student_id = request.session.get("student_id")
        student = student_registration.objects.get(id=student_id)
        stud_dept = student.department
        stud_sem = student.semester
        department = departments.objects.get(department_name=stud_dept)
        department_id = department.id

        feed = feedback.objects.filter(
            delete_status=0, department_pk_id=department_id, semester=stud_sem, is_flaged=0
        )
        feeds_app = feedback.objects.filter(
            delete_status=0, department_pk_id=department_id, is_flaged=1
        )

        feedback_html = render_to_string('student/partials/feedback_table.html', {'feed': feed})
        flagged_html = render_to_string('student/partials/flagged_feedback_table.html', {'feeds_app': feeds_app})

        return JsonResponse({
            'feedback_html': feedback_html, 
            'flagged_html': flagged_html, 
            'message': success_message
        })


    

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
