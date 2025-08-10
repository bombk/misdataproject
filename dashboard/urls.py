from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('master-parameters/', views.master_parameters, name='master_parameters'),
    path('data-upload/', views.data_upload, name='data_upload'),
    path('data-tables/', views.data_tables, name='data_tables'),
    path('api/dashboard-data/', views.api_dashboard_data, name='api_dashboard_data'),
    path('total-users/', views.total_user_list, name='total_user_list'),
    path('total-user-summary/', views.total_user_summary, name='total_user_summary'),
    path('total-transaction-summary/', views.total_transaction_summary, name='total_transaction_summary'),
    path('total-transactions/', views.total_transaction_list, name='total_transaction_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

