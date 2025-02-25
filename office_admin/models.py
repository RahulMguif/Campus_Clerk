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