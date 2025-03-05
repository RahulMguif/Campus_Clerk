from django.urls import path
from staff_incharge import views

urlpatterns = [
    path('staff_incharge_home/',views.staff_incharge_home,name='staff_incharge_home'),
    path('view_all_student/',views.view_all_student,name='view_all_student'),
    path('incharge_add_student/',views.incharge_add_student,name='incharge_add_student'),
    path('assign_programme_coordinator/', views.assign_programme_coordinator, name='assign_programme_coordinator'),
]