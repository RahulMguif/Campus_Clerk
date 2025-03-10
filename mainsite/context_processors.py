from mainsite.models import student_registration, staff_advisor, staff_incharge, hod

def global_user_details(request):
    context = {}

    # Student Details
    student_id = request.session.get('student_id')
    if student_id:
        student = student_registration.objects.filter(pk=student_id).first()
        context['student_profile_pic'] = student.profile_pic_url if student and student.profile_pic_url else 'admin/images/faces/avatar.jpg'
        context['student_name'] = student.fullname if student else ''
        context['student_email'] = student.email if student else ''

    # Staff Advisor Details
    staff_email = request.session.get('username')  # Assuming staff uses 'username' for login
    staff_advisor_obj = None  # Initialize variable

    if staff_email:
        staff_advisor_obj = staff_advisor.objects.filter(email=staff_email, delete_status=False).first()
        if staff_advisor_obj:
            context['staff_advisor_name'] = staff_advisor_obj.name
            context['staff_advisor_email'] = staff_advisor_obj.email

    # Staff In-Charge Details
    staff_incharge_obj = staff_incharge.objects.filter(email=staff_email, delete_status=False).first()
    if staff_incharge_obj:
        context['staff_incharge_name'] = staff_incharge_obj.name
        context['staff_incharge_email'] = staff_incharge_obj.email

    # HOD Details (Based on Department)
    if staff_advisor_obj and getattr(staff_advisor_obj, 'department_pk', None):
        hod_obj = hod.objects.filter(department_pk=staff_advisor_obj.department_pk, delete_status=False).first()
        if hod_obj:
            context['hod_name'] = hod_obj.name
            context['hod_email'] = hod_obj.email

    return context
