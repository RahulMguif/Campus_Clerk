from django.urls import path
from mainsite import views

urlpatterns = [
    path('', views.home_view,name='home'),
]