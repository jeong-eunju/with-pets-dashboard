import folium
import json
import numpy as np
from shapely.geometry import shape
from folium import Element

def generate_interactive_map(geojson_path, output_path):
    with open(geojson_path, encoding="utf-8") as f:
        geojson_data = json.load(f)

    m = folium.Map(location=[36.5, 128.8], zoom_start=7.5, tiles="cartodbpositron")

    gj = folium.GeoJson(
        geojson_data,
        name="경북 시군",
        style_function=lambda feature: {
            "fillColor": "#a7c8f2",
            "color": "#61738a",       # ✅ 테두리 색 연하게
            "weight": 0.8,              # ✅ 테두리 두께 얇게
            "opacity": 0.6,             # ✅ 테두리 투명도 낮추기
            "fillOpacity": 0.6
        },
        highlight_function=lambda feature: {
            "fillColor": "#5fa2e0",
            "color": "black",
            "weight": 3,
            "fillOpacity": 0.8
        }
    )
    gj.add_to(m)

    # ✅ 중심에 시군 이름 라벨 추가 (shapely 사용)
    for feature in geojson_data['features']:
        name = feature['properties'].get('행정구역', None)
        geometry = feature['geometry']

        if not name or not geometry:
            continue

        try:
            geom = shape(geometry)
            centroid = geom.centroid
            folium.Marker(
                location=[centroid.y - 0.015, centroid.x + 0.02],
                icon=folium.DivIcon(html=f'''
                    <div style="
                        display: inline-block;
                        font-size: 11px;
                        font-weight: bold;
                        color: black;
                        background-color: rgba(255, 255, 255, 0.3);
                        padding: 2px 6px;
                        border-radius: 4px;
                        white-space: nowrap;
                        text-align: center;
                        transform: translate(-50%, -50%);
                        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
                    ">
                        {name}
                    </div>
                ''')
            ).add_to(m)
        except Exception as e:
            print(f"⚠️ {name} 중심좌표 라벨 실패: {e}")

    # ✅ 클릭 이벤트 처리
    js = Element("""
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        let map;
        for (let key in window) {
            if (window[key] instanceof L.Map) {
                map = window[key];
                break;
            }
        }

        if (!map) {
            console.log("❌ Leaflet map 객체를 찾을 수 없습니다.");
            return;
        }

        map.eachLayer(function(layer) {
            if (layer.feature && layer.feature.properties && layer.feature.properties["행정구역"]) {
                layer.on('click', function(e) {
                    const region = layer.feature.properties["행정구역"];
                    console.log("✅ JS 클릭된 지역:", region);
                    if (region && window.parent) {
                        window.parent.postMessage(region, '*');
                    }
                });
            }
        });
    });
    </script>
    """)

    m.get_root().html.add_child(js)
    m.save(output_path)

def load_geojson(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
    
if __name__ == "__main__":
    generate_interactive_map(
        geojson_path="/Users/jeongeunju/Desktop/with-pets/dashboard/data/gyeongbuk_polygon_4326.geojson",
        output_path="/Users/jeongeunju/Desktop/with-pets/dashboard/www/gyeongbuk_map.html"
    )
