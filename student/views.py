from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.files.storage import FileSystemStorage
import traceback
from django.contrib import messages
from .models import *
from datetime import datetime, date, timedelta
from django.db import transaction
from django.db.models import F

# Create your views here.


def student_home(request):
    return render(request, 'student/home.html')

def application_form(request):
    try:
        current_user = request.session.get('student_id')
        if current_user == None:
            return redirect('404')
        
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
            course = request.POST.get('course')
            branch = request.POST.get('branch')
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


            # Check if the email already exists
            if student_application_request.objects.filter(student_email_address=student_email).exists():
                messages.error(request, 'This email is already associated with another application.')
                return render(request, 'student/student_application_form.html', {'application_number': application_number})

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
                                                                                 course = course,
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
                                                                                 application_status = 'Initial'
                                                                                 )
            print('registration POST Success')
            messages.success(request,
                             f'<strong>Your Application Submit Successfully..</strong><br>You will get a response within 48hr after review your application..')

            # contexts = {'username': user_nme, 'useremail': user_email}
            # return render(request, 'user_admin/registration.html', contexts)
            return render(request, 'student/student_application_form.html', {'application_number': application_number})
        else:
            print('registration ELSE')
            # contexts = {'username': user_nme, 'useremail': user_email}
            # return render(request, 'user_admin/registration.html', contexts)
            return render(request, 'student/student_application_form.html', {'application_number': application_number})


    except Exception as e:
        print('Exception registration', e)
        traceback_str = traceback.format_exc()
        print('\ntraceback_str', traceback_str)
        # contexts = {'username': user_nme, 'useremail': user_email}
        # return render(request, 'user_admin/registration.html', contexts)
        return render(request, 'student/student_application_form.html', {'application_number': application_number})
    