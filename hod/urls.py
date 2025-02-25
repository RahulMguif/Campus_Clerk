from django.urls import path
from hod import views

urlpatterns = [
    path('hod_home/',views.hod_home,name='hod_home')
    
]