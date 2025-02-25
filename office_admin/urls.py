from django.urls import path
from office_admin import views

urlpatterns = [
    path('admin_home/',views.admin_home,name='admin_home'),
    path('office_admin_login/',views.office_admin_login,name='office_admin_login'),
    path('logout/',views.logout_view,name='logout')
]