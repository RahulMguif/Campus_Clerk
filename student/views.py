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


# Create your views here.


def student_home(request):
    try:
        current_user = request.session.get('student_id')
        if current_user is None:
            return redirect('404')

        # Fetch the student details using the primary key
        student = student_registration.objects.filter(pk=current_user).first()
        
        if not student:
            return redirect('404')  # Redirect if student not found

        # Pass student data (fullname, email) to the template
        context = {
            'student_name': student.fullname,
            'student_email' : student.email,
            'profile_pic_url': student.profile_pic_url,  # Pass profile pic URL
        }
        return render(request, 'student/home.html', context)

    except Exception as e:
        print('Exception in student_home:', e)
        traceback_str = traceback.format_exc()
        print('\ntraceback_str:', traceback_str)
        return render(request, 'student/home.html')


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
        student=request.POST.get('student_id')
        student_obj=student_registration.objects.get(id=student)
        feed=feedback()
        feed.department_pk=department_obj
        feed.semester=semester
        feed.comment=comment
        feed.student_pk=student_obj
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
    # return HttpResponse(stud_dept)
    feed = feedback.objects.filter(delete_status=0, department_pk_id__department_name=stud_dept,is_flaged=0,semester=stud_sem)
    context={'feed':feed}
    return render(request,"student/feedback_view.html",context)



def flag_comment(request):
    if request.method=='POST':
        id=request.POST.get('flaged')
        flag=feedback.objects.get(id=id)
        flag.is_flaged=1
        flag.save()
        messages.success(request, 'Successfully flaged the comment')
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
