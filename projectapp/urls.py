"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views


urlpatterns = [
    path('get-active-locations/', views.GetActiveLocations.as_view(), name='get-active-locations'),
    path('get-all-locations/', views.GetAllLocationsView.as_view(), name='get-all-locations'),
    path('get-all-routes/', views.GetAllRoutesView.as_view(), name='get-all-routes'),
    path('get-all-locations_has_feedback/', views.GetAllLocaionsHasFeedbackView.as_view(), name='get-all-locations_has_feedback'),
    # path('all-projects/', views.ShowAllProjectsView.as_view(), name='all-projects'),
    # path('all-companies-active-days/', views.CompanyActiveDaysAPIView.as_view(), name='all-companies-active-days'),
    path("company-location-daterange/", views.CompanyLocationDateRangeAPIView.as_view(), name="company-location-daterange"),

    # dashboard
    path("days-per-month/all/", views.ProjectDaysPerMonthAllYearsView.as_view(), name="days-per-month-all"),
    path("company-location-range/all/", views.CompanyLocationRangesView.as_view(), name="company-location-range"),

    path('download-pdf/<int:project_id>/', views.download_latest_pdf, name='download_pdf'),

]
