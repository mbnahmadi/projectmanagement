import os
from datetime import date
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FeedBackAttachmentModel, FeedBackModel, FeedBackResponseModel
from .serializers import FeedBackAttachmentSerializer, ProjectFeedBackSerializer, CompanyFeedbackSerializer
from projectapp.models import ProjectModel
from rest_framework import status
from django.http import FileResponse, HttpResponseNotFound
from .services.feedback_service import get_company_feedback_activity
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer


class ProjectsFeedBack(APIView):
    # renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    # template_name = 'frontendapp/frontendapp/home.html'
    def get(self, request, id):
        # projects = ProjectModel.objects.filter(feedbacks__isnull=False)
        projects = ProjectModel.has_feedback.filter(id=id)
        # serializer = ProjectseFeedBackSerializer(project, many=True)
        serializer = ProjectFeedBackSerializer(projects, many=True, context={'request': request})
        # context = {
        #     'projects': serializer.data,
        #     'company': serializer.data[0]['company_name'] if serializer.data else None
        # }
        return Response(serializer.data, status=status.HTTP_200_OK)

class FeedBackCustomFilter(APIView):
    def get(self, request):
        company_name = request.query_params.get('company_name', None)
        location_name = request.query_params.get('location_name', None)
        start = request.query_params.get('start', None)
        end = request.query_params.get('end', None)
        # 
        if start or end:
            try:
                start = date.fromisoformat(start)
                end = date.fromisoformat(end)
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        result = get_company_feedback_activity(company_name, location_name, start, end)
        serializer = CompanyFeedbackSerializer(result, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)