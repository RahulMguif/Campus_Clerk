from django.db import models

# Create your models here.
class notification(models.Model):
    heading=models.CharField(max_length=100,null=True)
    description=models.CharField(max_length=600,null=True)
    document=models.CharField(max_length=300,null=True)
    enable=models.CharField(max_length=10,null=True)
    delete_status=models.CharField(max_length=5,null=True)
    date=models.DateTimeField(null=True)
    attendance_url=models.CharField(max_length=300,null=True)
    class Meta:
        db_table = 'notification'