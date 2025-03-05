from django.db import models
from staff_advisor.models import *
from hod.models import *
# Create your models here.

class student_registration(models.Model):
    fullname = models.CharField(max_length = 100, null=True)
    password = models.CharField(max_length = 100, null=True)
    email = models.EmailField(max_length=150)
    mobile = models.BigIntegerField(null=True)
    course = models.CharField(max_length = 100, null=True)
    department = models.CharField(max_length = 100, null=True)
    semester = models.CharField(max_length = 100, null=True)
    year_of_joining = models.CharField(max_length = 100, null=True)
    profile_pic_url = models.CharField(max_length = 200, null=True)
    is_active = models.BooleanField(default=False)
    is_class_rep = models.BooleanField(default=False, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    password_reset_token = models.CharField(max_length = 500, null=True)
    
    class Meta:
        db_table = 'student_registration'
        

class department_login(models.Model):
    hod_pk = models.ForeignKey(hod, on_delete=models.CASCADE, null=True)
    staff_advisor_pk = models.ForeignKey(staff_advisor, on_delete=models.CASCADE, null=True)
    staff_incharge_pk = models.ForeignKey(staff_incharge, on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length = 50, null=True)
    delete_status = models.BooleanField(default=False)

    class Meta:
        db_table = 'department_login'