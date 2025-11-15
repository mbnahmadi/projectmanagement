from django import forms
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point, LineString
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point, LineString
from .models import LocationModel, ProjectModel
# from core.latest_pdf import generate_latest_pdf_address


class GeometryTextArea(forms.Textarea):
    """
    Widget for manually entering LineString as 'lat1,lon1; lat2,lon2; ...'
    """
    # Widget -> در واقع کنترل می‌کنه چطور داده به کاربر نشون داده بشه و ازش گرفته بشه
    # برای نقطه و لاین و غیره  ویجت پیش فرض نقشه است
    def format_value(self, value):
        if isinstance(value, Point):
            return f"{value.y},{value.x}"
        elif isinstance(value, list):
            return "; ".join([f"{p.y},{p.x}" for p in value])
        return value

    def value_from_datadict(self, data, files, name):
        raw = data.get(name)
        if not raw:
            return None

        try:
            pairs = [p.strip() for p in raw.split(";") if p.strip()]
            points = []

            for pair in pairs:
                lat, lon = pair.split(",")
                points.append((float(lon), float(lat)))  

            if len(points) == 1:
                return Point(points[0]) 
            else:
                return LineString(points)  

        except Exception as e:
            raise forms.ValidationError(
                "Format is wrong. Example: "
                "Point → Lat,Lon | Line → Lat1,Lon1; Lat2,Lon2; Lat3,Lon3; ..."
                + str(e)
            )

class LocationAdminForm(forms.ModelForm):
    geometry_input = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
        required=False,
        label='Geometry Input',
        help_text='Enter as "lat,lon" for Point or "lat1,lon1; lat2,lon2; ..." for LineString'
    )

    class Meta:
        model = LocationModel
        fields = "__all__"
        # widgets = {
        #     'geometry': GeometryTextArea(attrs={"rows": 3, "cols": 40}),
        # }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.geometry:
            if self.instance.is_point():
                p = self.instance.geometry
                self.fields['geometry_input'].initial = f"{p.y},{p.x}"
            elif self.instance.is_line():
                coords = list(self.instance.geometry.coords)
                self.fields['geometry_input'].initial = "; ".join(
                f"{y},{x}" for (x, y) in coords
            )
                # self.fields['geometry_input'].initial = "; ".join([f"{p.y},{p.x}" for p in self.instance.geometry])

    def clean(self):
        cleaned_data = super().clean()
        raw_input = cleaned_data.get('geometry_input')
        
        if raw_input:
            try:
                pairs = [p.strip() for p in raw_input.split(";") if p.strip()]
                points = []
                for pair in pairs:
                    lat, lon = pair.split(",")
                    points.append((float(lon.strip()), float(lat.strip())))
                if len(points) == 1:
                    cleaned_data['geometry'] = Point(points[0], srid=4326)
                    # print('cleaned_data[geometry]', cleaned_data['geometry'])
                elif len(points) >= 2:
                    cleaned_data['geometry'] = LineString(points, srid=4326)
                else:
                    raise ValueError("At least 1 point required.")
            except Exception as e:
                raise ValidationError(f"Invalid geometry input: {str(e)}")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)  # اول instance آماده کن بدون save
        if 'geometry' in self.cleaned_data:  # اگر geometry بروز شده
            instance.geometry = self.cleaned_data['geometry']
            # print('instance.geometry', instance.geometry)

        if commit:
            instance.save()  # حالا save واقعی
            self.save_m2m()  # اگر m2m فیلدی داری
        return instance


# class ProjectAdminForm(forms.ModelForm):
#     project_address = forms.CharField(
#         required=False, 
#         help_text='please insert name of company and location in server. e.g-> AkamIndustry10Days_V01/SPD6',
#         label = 'project address in server'
#         )

#     class Meta:
#         model = ProjectModel
#         fields = "__all__"

#     def save(self, commit=True):
#         instance = super().save(commit=commit) # first save project_address 
#         if instance.project_address: # then 
#             pdf_path= instance.generate_latest_pdf_address()
#             if pdf_path:
#                 instance.latest_pdf_path = pdf_path
#                 instance.save(update_fields=['latest_pdf_path'])
#         return instance

