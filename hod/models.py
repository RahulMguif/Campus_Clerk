from django.db import models
from office_admin.models import *

class hod(models.Model):
    name = models.CharField(max_length = 100, null=True)
    email = models.EmailField(max_length=150)
    mobile = models.CharField(max_length=25,null=True)
    password = models.CharField(max_length = 100, null=True)
    is_active = models.IntegerField(null=True)
    password_reset_token = models.CharField(max_length = 500, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    delete_status = models.BooleanField(default=False)
    department_pk=models.ForeignKey(departments, on_delete=models.CASCADE,null=True, blank=True)
    class Meta:
        db_table = 'hod'

