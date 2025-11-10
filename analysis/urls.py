"""URL configuration for analysis dashboard."""
from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard_home, name='dashboard'),
    
    # Data exploration
    path('explorer/', views.data_explorer, name='data_explorer'),
    
    # Analysis jobs
    path('jobs/', views.jobs_list, name='jobs_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('run-analysis/', views.run_analysis, name='run_analysis'),
    
    # Legislator profiles
    path('legislator/<str:person_id>/', views.legislator_profile_view, name='legislator_profile'),
    path('legislators/search/', views.search_legislators, name='search_legislators'),
    
    # Ingestion logs
    path('ingestion-logs/', views.ingestion_logs, name='ingestion_logs'),
    
    # API endpoints
    path('api/job-status/<int:job_id>/', views.api_job_status, name='api_job_status'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
