import json
import folium
from folium import Element

def main():
    # 1. خواندن مرز جغرافیایی استان فارس
    with open("fars.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # 2. ایجاد نقشه با مرکزیت استان فارس
    m = folium.Map(
        location=[29.6, 53.0],
        zoom_start=7,
        tiles=None
    )

    # لایه‌های نقشه پایه (بدون نیاز به کلید و بدون واترمارک)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="تصویر ماهواره‌ای",
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="OpenStreetMap contributors",
        name="نقشه راه‌ها",
        overlay=False,
        control=True
    ).add_to(m)

    # 3. لایه WMS مستقیم شاخص رسمی و محاسبه‌شده FWI از سازمان پایش آتش اتحادیه اروپا/جهانی (EFFIS)
    folium.WmsTileLayer(
        url="https://ies-ows.jrc.ec.europa.eu/effis",
        layers="ecmwf007.fwi",
        fmt="image/png",
        transparent=True,
        opacity=0.65,
        name="شاخص FWI محاسبه‌شده جهانی (EFFIS/ECMWF)",
        overlay=True,
        control=True
    ).add_to(m)

    # 4. انداختن کادر مرز استان فارس روی لایه
    folium.GeoJson(
        geojson_data,
        name="مرز استان فارس",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "#d90429",
            "weight": 2.5,
            "dashArray": "4, 4"
        }
    ).add_to(m)

    # 5. راهنمای تصویری رسمی رده‌بندی FWI
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000; background: white;
                padding: 12px 16px; border-radius: 8px; border: 1px solid #ccc; font-family: Tahoma;
                direction: rtl; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
        <b style="font-size: 13px;">شاخص خطر آتش‌سوزی (FWI)</b><br>
        <span style="font-size: 11px; color: #666;">منبع: لایه ماهواره‌ای ECMWF / EFFIS</span>
        <hr style="margin: 6px 0;">
        <i style="background:#2b83ba; width:15px; height:15px; float:right; margin-left:8px; opacity:0.8;"></i> بسیار کم (Very Low)<br>
        <i style="background:#abdda4; width:15px; height:15px; float:right; margin-left:8px; opacity:0.8;"></i> کم (Low)<br>
        <i style="background:#ffffbf; width:15px; height:15px; float:right; margin-left:8px; opacity:0.8;"></i> متوسط (Moderate)<br>
        <i style="background:#fdae61; width:15px; height:15px; float:right; margin-left:8px; opacity:0.8;"></i> بالا (High)<br>
        <i style="background:#d7191c; width:15px; height:15px; float:right; margin-left:8px; opacity:0.8;"></i> بسیار بالا (Very High)<br>
        <i style="background:#7a0177; width:15px; height:15px; float:right; margin-left:8px; opacity:0.8;"></i> بحرانی (Extreme)
    </div>
    """
    m.get_root().html.add_child(Element(legend_html))
    folium.LayerControl(position="topright").add_to(m)

    m.save("index.html")
    print("Map generated with official pre-calculated FWI WMS layer.")

if __name__ == "__main__":
    main()
