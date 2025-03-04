from django.db import models


class course(models.Model):
    course_name = models.CharField(max_length = 200, null=True)
    delete_status = models.BooleanField(default=False)
    class Meta:
        db_table = 'course'


class departments(models.Model):
    course_pk=models.ForeignKey(course, on_delete=models.CASCADE)
    department_name = models.CharField(max_length = 200, null=True)
    delete_status = models.BooleanField(default=False)
   
    class Meta:
        db_table = 'departments'   
             
class office_admin(models.Model):
    username=models.CharField(max_length=100,null=True)
    password=models.CharField(max_length=100,null=True)
    is_superuser=models.IntegerField()
    
    class Meta:
        db_table = 'office_admin'
        
        
class feedback_enable(models.Model):
    enable_status = models.BooleanField(default=False)
    class Meta:
        db_table = 'feedback_enable'


class event(models.Model):
    event_name = models.CharField(max_length = 200, null=True)
    delete_status = models.BooleanField(default=False)
    class Meta:
        db_table = 'event'  


class staff_incharge(models.Model):
    name = models.CharField(max_length = 100, null=True)
    email = models.EmailField(max_length=150)
    mobile = models.CharField(max_length=25,null=True)
    password = models.CharField(max_length = 100, null=True)
    is_active = models.IntegerField(null=True)
    password_reset_token = models.CharField(max_length = 500, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    delete_status = models.BooleanField(default=False)
    department_pk=models.ForeignKey(departments, on_delete=models.CASCADE, null=True, blank=True)
    event_pk=models.ForeignKey(event, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        db_table = 'staff_incharge'