from django.urls import path
from staff_incharge import views

urlpatterns = [
    path('staff_incharge_home/',views.staff_incharge_home,name='staff_incharge_home'),
    path('view_all_student/',views.view_all_student,name='view_all_student'),
    path('incharge_add_student/',views.incharge_add_student,name='incharge_add_student'),
    path('assign_programme_coordinator/', views.assign_programme_coordinator, name='assign_programme_coordinator'),
    path('add_notification/',views.add_notification, name='add_notification'),
    path('notification_delete/',views.notification_delete,name='notification_delete'),
    path('event_participants/',views.event_participants,name='event_participants'),
    path('add-student/', views.add_student_to_event, name='add_student_to_event'),
]