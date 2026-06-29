import os
from datetime import date
from django.shortcuts import render
from django.template import context
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views import View
from .models import CompanyModel, ProjectModel
from .services.project_service import get_company_points_activity
from .services.dashboard import calculate_days_per_month_all_years, get_company_location_ranges
from rest_framework import status
from django.http import FileResponse, HttpResponseNotFound
from .serializers import CompanyPointsActivitySerializer, ProjectSerializers
from django.db.models import CharField, Func

class GeometryType(Func):
    function = 'ST_GeometryType' 
    output_field = CharField()

# Create your views here.

class GetActiveLocations(APIView):
    '''
    get all active locations
    '''
    def get(self, request):
        try:
            active = ProjectModel.active_locations.all()
            serializer = ProjectSerializers(active, many=True)
            return Response(serializer.data)
        except ProjectModel.DoesNotExist:
            return Response({"error": "no active location found."}, status=404)

class GetAllLocationsView(APIView):
    '''
    get all locations
    '''
    def get(self, request):
        try:
            locations = ProjectModel.objects.all()
            serializer = ProjectSerializers(locations, many=True)
            return Response(serializer.data)
        except ProjectModel.DoesNotExist:
            return Response({"error": "no location found."}, status=404)

class GetAllRoutesView(APIView):
    '''
    get all routes
    '''
    def get(self, request):
        try:
            routes = ProjectModel.objects.annotate(
                geom_type=GeometryType('location_name__geometry')
            ).filter(geom_type='ST_LineString')
            serializer = ProjectSerializers(routes, many=True)

            return Response(serializer.data)
        except ProjectModel.DoesNotExist:
            return Response({"error": "no route found."}, status=404)

class GetAllLocaionsHasFeedbackView(APIView):
    def get(self, request):
        try:
            fb = ProjectModel.has_feedback.all()
            serializer = ProjectSerializers(fb, many=True)
            return Response(serializer.data)
        except ProjectModel.DoesNotExist:
            return Response({"error": "no active location found."}, status=404)

        # 

def download_latest_pdf(request, project_id):
    '''
    download latest pdf of active project
    '''
    project = ProjectModel.active_locations.get(id=project_id)
    if project.latest_pdf_path and os.path.exists(project.latest_pdf_path):
        filename = os.path.basename(project.latest_pdf_path)
        response = FileResponse(open(project.latest_pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponseNotFound("No PDF available")

class CompanyLocationDateRangeAPIView(APIView):
    """
    API برای محاسبه تعداد روزهای یکتای فعال بودن هر شرکت در بازه داده شده
    """

    def get(self, request, *args, **kwargs):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        company_name = request.query_params.get("company_name")
        location_name = request.query_params.get("location_name")

        if start or end:
            try:
                start = date.fromisoformat(start)
                end = date.fromisoformat(end)
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        result = get_company_points_activity(company_name, location_name, start, end)
        # print(result)

        serializer = CompanyPointsActivitySerializer(result, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# @cache_page
class ProjectDaysPerMonthAllYearsView(APIView):
    """
    Return number of project days grouped by month for all available years.
    """
    def get(self, request):
        try:
            year = request.query_params.get('year')
            data = calculate_days_per_month_all_years(filter_year=year)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyLocationRangesView(APIView):
    """
    Return number of project days grouped by month for all available years.
    """
    def get(self, request):
        try:
            company_name_filter = request.query_params.get("company", None)
            data = get_company_location_ranges(company_name_filter)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)