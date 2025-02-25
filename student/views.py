from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.core.files.storage import FileSystemStorage
import traceback
from django.contrib import messages
from .models import *
from datetime import datetime, date, timedelta

# Create your views here.


def student_home(request):
    return render(request, 'student/home.html')

def application_form(request):
    try:
        # return redirect('it_pricing')
        current_user = request.session.get('student_id')
        if current_user == None:
            return redirect('404')
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

            if 'student_sign' in request.FILES:
                signature_scanned_copy_file = request.FILES['student_sign']
                fs = FileSystemStorage(
                    location='media/attached_signature')  # Location is useed to define a folder to save file inside the media folder
                attached_sign = fs.save(signature_scanned_copy_file.name, signature_scanned_copy_file)
                attached_sign_url = fs.base_location + '/' + attached_sign  # URl Retriving for DB Storing .baseurl is an inbuilt function
                print('Attached signature saved into folder')
            else:
                print('Else aadhar_card_copy URL')
                signature_scanned_copy_file = 'No signature is uploaded'
                attached_sign_url = 'File is not upload by user'  # In Exceptional case 'File is not upload by user'

            if 'reason_document' in request.FILES:
                document_scanned_copy_file = request.FILES['reason_document']
                fs = FileSystemStorage(
                    location='media/attached_proofs')  # Location is useed to define a folder to save file inside the media folder
                attached_proof = fs.save(document_scanned_copy_file.name, document_scanned_copy_file)
                attached_proof_url = fs.base_location + '/' + attached_proof  # URl Retriving for DB Storing .baseurl is an inbuilt function
                print('Attached proof saved into folder')
            else:
                print('Else aadhar_card_copy URL')
                document_scanned_copy_file = 'No attachments is not uploaded'
                attached_sign_url = 'File is not upload by user'  # In Exceptional case 'File is not upload by user'

            

            print('=========================CERTIFICATE DETAILS=========================')
            print('Attached Proof file', document_scanned_copy_file)
            print('Attached Proof URL', attached_proof_url)

            print('Attached signature file', document_scanned_copy_file)
            print('Attached signature URL', attached_sign_url)


            row_count = student_application_request.objects.count()
            if row_count == 0:
                application_number = 1
            else:
                application_number = student_application_request.objects.last().id
                application_number = application_number + 1
            print('application_number', application_number)
            date_today = date.today()  # get date for compain the Application ID
            date_today = date_today.strftime('%Y%m%d')  # remove - from date
            date_today = date_today[
                         2:]  # Remove first 2 character from date because we need to trim the 20 from year 2023
            application_id = 'AP' + str(date_today) + 'CC' + str(
                application_number)  # str is used to convert ID to string.
            
            # Applied date id using for date
            print('Application ID genarated it is, Application_id : ', application_id)

            new_application_request = student_application_request.objects.create(student_pk = current_user,
                                                                                 student_application_no = application_id,
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
            return render(request, 'student/student_application_form.html')
        else:
            print('registration ELSE')
            # contexts = {'username': user_nme, 'useremail': user_email}
            # return render(request, 'user_admin/registration.html', contexts)
            return render(request, 'student/student_application_form.html')


    except Exception as e:
        print('Exception registration', e)
        traceback_str = traceback.format_exc()
        print('\ntraceback_str', traceback_str)
        # contexts = {'username': user_nme, 'useremail': user_email}
        # return render(request, 'user_admin/registration.html', contexts)
        return render(request, 'student/student_application_form.html')
    