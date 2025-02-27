from django.urls import path
from staff_advisor import views

urlpatterns = [
    path('staff_home/',views.staff_home,name='staff_home'),

]