import json
from datetime import datetime, timedelta
import folium
from folium import Element

def main():
    # 1. خواندن مرز جغرافیایی استان فارس
    with open("fars.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # تاریخ روز جاری یا دیروز برای فراخوانی لایه ماهواره‌ای ناسا
    today_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 2. ایجاد نقشه پایه با مرکزیت استان فارس
    m = folium.Map(
        location=[29.6, 53.0],
        zoom_start=7,
        tiles=None
    )

    # نقشه ماهواره‌ای باکیفیت Esri
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="تصویر ماهواره‌ای",
        overlay=False,
        control=True
    ).add_to(m)

    # نقشه توپوگرافی و راه‌ها
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="OpenStreetMap contributors",
        name="نقشه راه‌ها و توپوگرافی",
        overlay=False,
        control=True
    ).add_to(m)

    # 3. لایه پایش حرارتی و حریق ناسا (NASA GIBS / VIIRS Thermal Anomalies)
    nasa_fire_url = (
        "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
        "VIIRS_SNPP_Thermal_Anomalies_375m_All/default/"
        f"{today_str}/GoogleMapsCompatible_Level8/{{z}}/{{y}}/{{x}}.png"
    )
    folium.TileLayer(
        tiles=nasa_fire_url,
        attr="NASA Global Imagery Browse Services (GIBS)",
        name="نقاط داغ و پایش حرارتی ناسا (VIIRS)",
        overlay=True,
        control=True,
        opacity=0.9
    ).add_to(m)

    # 4. ترسیم خط مرزی استان فارس
    folium.GeoJson(
        geojson_data,
        name="مرز استان فارس",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "#e63946",
            "weight": 3,
            "dashArray": "5, 5"
        }
    ).add_to(m)

    # 5. راهنمای نقشه
    legend_html = f"""
    <div style="position: fixed; bottom: 25px; left: 25px; z-index: 1000; background: rgba(255,255,255,0.95);
                padding: 12px 16px; border-radius: 8px; border: 1px solid #bbb; font-family: Tahoma;
                direction: rtl; font-size: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.25);">
        <b style="font-size: 13px; color: #1d3557;">سامانه پایش خطر حریق استان فارس</b><br>
        <span style="font-size: 11px; color: #555;">منبع داده: ماهواره‌های پایش حریق NASA GIBS</span>
        <hr style="margin: 6px 0; border-top: 1px solid #ddd;">
        <span style="display: inline-block; width: 12px; height: 12px; background: #e63946; border-radius: 50%; margin-left: 6px;"></span>
        پایش و انطباق روزانه: <b>{today_str}</b>
    </div>
    """
    m.get_root().html.add_child(Element(legend_html))
    folium.LayerControl(position="topright").add_to(m)

    m.save("index.html")
    print("Map built successfully with live NASA layer.")

if __name__ == "__main__":
    main()
