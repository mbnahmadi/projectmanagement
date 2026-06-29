from pydoc import source_synopsis
from rest_framework import serializers
# from feedbackapp.serializers import FeedBackAttachmentSerializer
from .models import CompanyModel, ProjectModel
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField
from feedbackapp.serializers import FeedBackSerializer


class ProjectSerializers(GeoFeatureModelSerializer):
    company_name = serializers.CharField(source='company_name.name')
    days_format = serializers.CharField(source='days_format.format_name')
    project_format = serializers.CharField(source='project_format.name')
    location_name = serializers.CharField(source='location_name.name')
    geometry = GeometryField(source='location_name.geometry')
    has_feedback = serializers.SerializerMethodField()

    def get_has_feedback(self, obj):
        return obj.feedbacks.exists()

    class Meta:
        model = ProjectModel
        geo_field = 'geometry'
        fields = ['pk', 'company_name', 'project_format', 'geometry', 'location_name', 'is_active_now', 'start_date', 'end_date', 'days_format', 'has_feedback']


class PointActivitySerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    location_name = serializers.CharField()
    project_format = serializers.CharField()
    geometry = GeometryField()
    start_date = serializers.CharField()
    end_date = serializers.CharField()
    days_format = serializers.CharField()
    is_active_now = serializers.BooleanField()
    active_days = serializers.IntegerField()


class CompanyPointsActivitySerializer(serializers.Serializer):
    company_name = serializers.CharField()
    detail = PointActivitySerializer(many=True)
    total_days = serializers.IntegerField()
    total_location = serializers.IntegerField()







