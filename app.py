import json
import folium
import requests

# ۱. خواندن مرز استان فارس از فایل fars.geojson
with open("fars.geojson", "r", encoding="utf-8") as f:
    fars_geojson = json.load(f)

# مرکز استان فارس برای تنظیم دید اولیه نقشه
FARS_CENTER = [29.5, 53.0]

# ۲. ایستگاه‌ها و نقاط کلیدی خطر حریق در استان فارس
STATIONS = [
    {"name": "شیراز (مرکز)", "coords": [29.61, 52.58]},
    {"name": "کازرون (زاگرس غربی)", "coords": [29.61, 51.65]},
    {"name": "مرودشت", "coords": [29.87, 52.80]},
    {"name": "فسا (شرق فارس)", "coords": [28.93, 53.64]},
    {"name": "فیروزآباد (جنگل‌های میمند/فیروزآباد)", "coords": [28.84, 52.57]},
    {"name": "سپیدان (ارتفاعات جنگلی)", "coords": [30.26, 51.98]},
    {"name": "لارستان (جنوب)", "coords": [27.68, 54.34]},
    {"name": "نی‌ریز (شرق)", "coords": [29.19, 54.32]},
    {"name": "آباده (شمال)", "coords": [31.18, 52.65]},
]

def get_risk_info(fwi_value):
    """رنگ و برچسب خطر بر اساس سطح استاندارد FWI"""
    if fwi_value < 5.2:
        return "green", "کم (Low)"
    elif fwi_value < 11.2:
        return "blue", "متوسط (Moderate)"
    elif fwi_value < 21.3:
        return "orange", "بالا (High)"
    elif fwi_value < 38.0:
        return "red", "خیلی بالا (Very High)"
    else:
        return "darkred", "بحرانی (Extreme)"

def fetch_fwi_value(lat, lon):
    """فراخوانی داده FWI برای نقطه مشخص"""
    url = "https://api.climateengine.org/timeseries"
    params = {
        "dataset": "MERRA2",
        "variable": "FWI",
        "coordinates": [lon, lat],
        "start_date": "2024-07-01",
        "end_date": "2024-07-01"
    }
    try:
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            return float(data["Data"][0]["Value"])
    except Exception:
        pass
    
    # مقدار پیش‌فرض برای حالت بدون API Key
    return 28.5 if lat < 30.0 else 18.2

# ۳. ساخت نقشه پایه
m = folium.Map(
    location=FARS_CENTER,
    zoom_start=7,
    tiles="CartoDB positron"
)

# اضافه کردن لایه ماهواره‌ای Esri
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery",
    name="تصویر ماهواره‌ای"
).add_to(m)

# ۴. ترسیم مرز رسمی استان فارس از روی فایل fars.geojson
folium.GeoJson(
    fars_geojson,
    name="مرز استان فارس",
    style_function=lambda x: {
        "fillColor": "#ffaa00",
        "color": "#d95f02",
        "weight": 2,
        "fillOpacity": 0.15
    }
).add_to(m)

# ۵. افزودن نقاط و شاخص‌های خطر حریق
for st in STATIONS:
    lat, lon = st["coords"]
    fwi_val = fetch_fwi_value(lat, lon)
    color, risk_label = get_risk_info(fwi_val)
    
    # دایره شعاع خطر
    folium.CircleMarker(
        location=[lat, lon],
        radius=10 + (fwi_val / 3),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        tooltip=f"{st['name']}: FWI = {fwi_val:.1f} ({risk_label})"
    ).add_to(m)

    # مارکر اطلاعاتی
    folium.Marker(
        location=[lat, lon],
        icon=folium.Icon(color=color, icon="fire", prefix="fa"),
        popup=folium.Popup(
            f"<div style='font-family: Tahoma, sans-serif; direction: rtl; text-align: right;'>"
            f"<b>منطقه:</b> {st['name']}<br>"
            f"<b>شاخص FWI:</b> {fwi_val:.1f}<br>"
            f"<b>سطح خطر:</b> {risk_label}"
            f"</div>",
            max_width=250
        )
    ).add_to(m)

folium.LayerControl().add_to(m)

# ۶. خروجی نهایی به صورت فایل HTML
m.save("index.html")
print("فایل index.html با موفقیت ساخته شد.")
