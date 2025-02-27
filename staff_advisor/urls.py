from django.urls import path
from staff_advisor import views

urlpatterns = [
    path('staff_home/',views.staff_home,name='staff_home'),
    path('staff_advisor_login/',views.staff_advisor_login,name='staff_advisor_login'),
]