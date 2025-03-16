from django.db import models
from mainsite.models import student_registration
from staff_advisor.models import *
from hod.models import *
from office_admin.models import *



# Student application model

class student_application_request(models.Model):
    student_pk = models.ForeignKey(student_registration, on_delete=models.CASCADE)
    student_application_no = models.CharField(max_length=50, null=True)
    full_name = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length = 20, null=True)
    course = models.CharField(max_length=100, null=True) # eg: M-Tech, B-Tech
    branch = models.CharField(max_length=100, null=True) # eg: CS, ECE
    admission_no = models.CharField(max_length=50, null=True)
    admission_date = models.DateField(null=True)
    university = models.CharField(max_length=100, null=True)
    university_reg_no = models.CharField(max_length=100, null=True)
    semester = models.IntegerField(null=True)
    hostel_name = models.CharField(max_length=100, null=True)
    hostel_admission_date = models.DateField(null=True)
    tc_no = models.CharField(max_length=100, null=True)
    tc_date = models.DateField(null=True)
    apply_for = models.CharField(max_length=100, null=True) # certificate services
    reason = models.CharField(max_length=100, null=True)
    contact_address = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=100, null=True)
    student_signature_url = models.CharField(max_length = 150, null=True)
    student_email_address = models.CharField(max_length = 150, null=True)
    staff_advisor_pk = models.ForeignKey(staff_advisor, on_delete=models.CASCADE, null=True)
    staff_advisor_remark = models.CharField(max_length = 150, null=True)
    staff_advisor_signature_url = models.CharField(max_length = 150, null=True)
    staff_approval_status = models.CharField(max_length=20, null=True)
    staff_approval_date = models.DateField(null=True)
    hod_pk = models.ForeignKey(hod, on_delete=models.CASCADE, null=True)
    hod_remark = models.CharField(max_length = 150, null=True)
    hod_signature_url = models.CharField(max_length = 150, null=True)   
    hod_approval_status = models.CharField(max_length=20, null=True)
    hod_approval_date = models.DateField(null=True)
    office_remark = models.CharField(max_length = 150, null=True)
    office_signature_url = models.CharField(max_length = 150, null=True)   
    office_approval_status = models.CharField(max_length=20, null=True)
    office_approval_date = models.DateField(null=True)
    application_submitted_date = models.DateTimeField(null=True)
    application_status = models.CharField(max_length=20, null=True)
    delete_status = models.BooleanField(default=False)

    class Meta:
        db_table = 'student_application_request'


# Student feedback model

class feedback(models.Model):
    department_pk = models.ForeignKey(departments, on_delete=models.CASCADE, null=True) # eg: CS, ECE
    semester = models.IntegerField(null=True)
    comment = models.CharField(max_length=1100)
    feedback_for = models.CharField(max_length=50, null=True)
    is_flaged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=100, null=True)
    submitted_date = models.DateTimeField(null=True)
    delete_status = models.CharField(max_length=50)

    class Meta:
        db_table = 'feedback'
        

class office_documents(models.Model):
    document_name = models.CharField(max_length = 200, null=True)
    document_url = models.CharField(max_length = 150, null=True)  
    reason = models.CharField(max_length=150, null=True)
    student_pk=models.ForeignKey(student_registration, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        db_table = 'office_documents'          