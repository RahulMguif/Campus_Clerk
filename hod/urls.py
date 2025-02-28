from django.urls import path
from hod import views

urlpatterns = [
    path('hod_home/',views.hod_home,name='hod_home'),
    path('review_application/',views.review_application,name='review_application'),
    path('update_application_hod/<int:application_id>/',views.update_application_hod,name='update_application_hod'),
    path('approval_status_hod/<int:application_pk>/',views.approval_status_hod,name='approval_status_hod'),

    
]