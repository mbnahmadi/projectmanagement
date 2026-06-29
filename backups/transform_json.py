# import json
# from django.contrib.gis.geos import Point

# with open('projects.json', encoding="utf8") as f:
#     data = json.load(f)

# new_data = []
# for obj in data:
#     fields = obj["fields"]

#     # Build geometry field
#     lat = fields.pop("lat", None)
#     lon = fields.pop("lon", None)
#     if lat is not None and lon is not None:
#         fields["geometry"] = str(Point(lon, lat))  # "POINT(lon lat)"

#     # Rename file field
#     fields["attachment"] = fields.pop("image_description", None)

#     # Add latest_pdf_path (empty for now)
#     fields["latest_pdf_path"] = None

#     obj["fields"] = fields
#     new_data.append(obj)

# with open("new_projects.json", "w") as f:
#     json.dump(new_data, f, indent=2)


import json
import hashlib

# فایل بکاپ اصلی
INPUT_FILE = "ProjectModel.json"
# فایل‌های خروجی
LOCATIONS_FILE = "locations.json"
PROJECTS_FILE = "new_projects.json"

with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

locations = []
projects = []

# برای جلوگیری از تکراری شدن لوکیشن‌ها
location_map = {}
next_loc_pk = 1

for obj in data:
    if obj["model"] == "projectapp.projectmodel":
        fields = obj["fields"]
        loc_name = fields.pop("location", None)
        geom = fields.pop("geometry", None)

        if loc_name and geom:
            # یک کلید یکتا برای تشخیص لوکیشن تکراری
            key = hashlib.sha1((loc_name + geom).encode()).hexdigest()

            if key not in location_map:
                location_map[key] = next_loc_pk
                locations.append({
                    "model": "projectapp.locationmodel",
                    "pk": next_loc_pk,
                    "fields": {
                        "name": loc_name,
                        "geometry": geom
                    }
                })
                next_loc_pk += 1

            # ست کردن فیلد location به pk درست
            fields["location"] = location_map[key]

        projects.append(obj)
    else:
        # مدل‌های دیگر بدون تغییر منتقل شوند
        projects.append(obj)

# ذخیره فایل‌های خروجی
with open(LOCATIONS_FILE, "w", encoding="utf-8") as f:
    json.dump(locations, f, ensure_ascii=False, indent=2)

with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)

print(f"✅ Done!\n- {len(locations)} locations saved to {LOCATIONS_FILE}\n- {len(projects)} projects saved to {PROJECTS_FILE}")
