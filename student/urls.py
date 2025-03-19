from django.urls import path
from student import views

urlpatterns = [
    path('student_dashboard/', views.student_home, name='student_dashboard'),
    path('student_application/', views.application_form, name='student_application'),
    path('add_feedback/',views.add_feedback,name='add_feedback'),
    path('my_applications/', views.my_applications, name='my_applications'),
    path('feedback_view/',views.feedback_view,name='feedback_view'),
    path('flag_comment',views.flag_comment,name='flag_comment'),
    path('edit_profile',views.edit_profile,name='edit_profile'),
    
    path('add_feedback/',views.add_feedback,name='add_feedback'),
    path('view_documents/',views.view_documents,name='view_documents'),
    
    path('notification_view/',views.notification_view,name='notification_view'),
    path('add_announcement/',views.add_announcement,name='add_announcement'),
    path('delete_announcement/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),
    path('add_attendance/',views.add_attendance,name='add_attendance'),
    path('notification/apply/<int:pk>/', views.apply_notification, name='apply_notification'),
    path('notification/submit/', views.submit_application, name='submit_application'),


]