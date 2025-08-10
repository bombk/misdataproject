from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('master-parameters/', views.master_parameters, name='master_parameters'),
    path('data-upload/', views.data_upload, name='data_upload'),
    path('data-tables/', views.data_tables, name='data_tables'),
    path('api/dashboard-data/', views.api_dashboard_data, name='api_dashboard_data'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

