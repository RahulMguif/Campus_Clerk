from django.db import models



class course(models.Model):
    course_name = models.CharField(max_length = 200, null=True)
    delete_status = models.BooleanField(default=False)
    class Meta:
        db_table = 'course'


class departments(models.Model):
    couse_pk=models.ForeignKey(course, on_delete=models.CASCADE)
    department_name = models.CharField(max_length = 200, null=True)
    delete_status = models.BooleanField(default=False)
   
    class Meta:
        db_table = 'departments'        