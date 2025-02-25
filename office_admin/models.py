from django.db import models

# Create your models here.
class office_admin(models.Model):
    username=models.CharField(max_length=100,null=True)
    password=models.CharField(max_length=100,null=True)
    is_superuser=models.IntegerField()
    
    class Meta:
        db_table = 'office_admin'