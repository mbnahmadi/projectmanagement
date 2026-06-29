import requests
import os
import math
import time
import random

def deg2num(lat, lon, zoom):
    lat_r = math.radians(lat)
    n = 2 ** zoom
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.log(math.tan(lat_r) + 1/math.cos(lat_r)) / math.pi) / 2 * n)
    x = max(0, min(n - 1, x))
    y = max(0, min(n - 1, y))
    return x, y

def download_tiles(zoom_levels, lat_min, lat_max, lon_min, lon_max):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://basemaps.cartocdn.com/"
    }

    for z in zoom_levels:
        x1, y1 = deg2num(lat_max, lon_min, z)
        x2, y2 = deg2num(lat_min, lon_max, z)
        y_start, y_end = min(y1, y2), max(y1, y2)

        print(f"--- start downloading zoom {z} ---")
        for x in range(x1, x2 + 1):
            for y in range(y_start, y_end + 1):
                path = f"tiles/{z}/{x}"
                os.makedirs(path, exist_ok=True)
                filepath = f"{path}/{y}.png"

                if os.path.exists(filepath):
                    continue

                try:
                    url = f"https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
                    
                    r = requests.get(url, headers=headers, timeout=15)
                    
                    if r.status_code == 200:
                        with open(filepath, "wb") as f:
                            f.write(r.content)
                        print(f"zoom {z} -> {x}/{y}")
                    elif r.status_code == 403:
                        print("error 403")
                        return
                    else:
                        print(f"error {r.status_code} for {z}/{x}/{y}")
                except Exception as e:
                    print(f"error {e}")

                time.sleep(random.uniform(0.1, 0.3))

download_tiles(
    zoom_levels=range(1, 10),
    lat_min=23.0,
    lat_max=42.5,
    lon_min=43.5,
    lon_max=64.0
)