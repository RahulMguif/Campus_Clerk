from mainsite.models import student_registration
from hod.models import *
from staff_advisor.models import *
from office_admin.models import *


def global_user_details(request):
    context = {}

    # ===================== Student Details ============================
    student_id = request.session.get('student_id')
    if student_id:
        student = student_registration.objects.filter(pk=student_id).first()
        context['student_profile_pic'] = student.profile_pic_url if student and student.profile_pic_url else 'admin/images/faces/avatar.jpg'
        context['student_name'] = student.fullname if student else ''
        context['student_email'] = student.email if student else ''

    # ===================== Staff Advisor Details =======================
    staff_email = request.session.get('username')  # Assuming staff uses 'username' for login
    staff_advisor_obj = None

    if staff_email:
        # Fetch Staff Advisor Details
        staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()
        if staff_advisor_obj:
            context['staff_advisor_name'] = staff_advisor_obj.name
            context['staff_advisor_email'] = staff_advisor_obj.email

    # ===================== Staff In-Charge Details =====================
    staff_incharge_obj = staff_incharge.objects.filter(email=staff_email, delete_status=False).first()
    if staff_incharge_obj:
        context['staff_incharge_name'] = staff_incharge_obj.name
        context['staff_incharge_email'] = staff_incharge_obj.email

    # ===================== HOD Details =====================
    # Fetch HOD Details based on the logged-in user's role
    if staff_advisor_obj:
        # If the user is a staff advisor, fetch the HOD based on their department
        if staff_advisor_obj.department_pk:
            department_id = staff_advisor_obj.department_pk.id
            hod_obj = hod.objects.filter(department_pk_id=department_id, delete_status=False).first()
            if hod_obj:
                context['hod_name'] = hod_obj.name
                context['hod_email'] = hod_obj.email
            else:
                context['hod_name'] = "N/A"
                context['hod_email'] = "N/A"
        else:
            context['hod_name'] = "N/A"
            context['hod_email'] = "N/A"
    elif staff_incharge_obj:
        # If the user is a staff in-charge, fetch the HOD based on their department
        if staff_incharge_obj.department_pk:
            department_id = staff_incharge_obj.department_pk.id
            hod_obj = hod.objects.filter(department_pk_id=department_id, delete_status=False).first()
            if hod_obj:
                context['hod_name'] = hod_obj.name
                context['hod_email'] = hod_obj.email
            else:
                context['hod_name'] = "N/A"
                context['hod_email'] = "N/A"
        else:
            context['hod_name'] = "N/A"
            context['hod_email'] = "N/A"
    else:
        # If the user is a HOD, fetch their own details
        hod_obj = hod.objects.filter(email=staff_email, delete_status=False).first()
        if hod_obj:
            context['hod_name'] = hod_obj.name
            context['hod_email'] = hod_obj.email
        else:
            context['hod_name'] = "N/A"
            context['hod_email'] = "N/A"

    return context