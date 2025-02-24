from django.db import models

# Create your models here.

class student_registration(models.Model):
    fullname = models.CharField(max_length = 100, null=True)
    password = models.CharField(max_length = 100, null=True)
    email = models.EmailField(max_length=150)
    mobile = models.BigIntegerField(null=True)
    department = models.CharField(max_length = 100, null=True)
    semester = models.CharField(max_length = 100, null=True)
    year_of_joining = models.CharField(max_length = 100, null=True)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    password_reset_token = models.CharField(max_length = 500, null=True)
    
    class Meta:
        db_table = 'student_registration'
        
