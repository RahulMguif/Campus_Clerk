from django.db import models

class staff_advisor(models.Model):
    name = models.CharField(max_length = 100, null=True)
    email = models.EmailField(max_length=150)
    mobile = models.CharField(max_length=25,null=True)
    password = models.CharField(max_length = 100, null=True)
    is_active = models.IntegerField(null=True)
    password_reset_token = models.CharField(max_length = 500, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    delete_status = models.BooleanField(default=False)
    class Meta:
        db_table = 'staff_advisor'
