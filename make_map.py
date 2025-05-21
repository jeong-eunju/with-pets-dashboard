# import geopandas as gpd
# from shapely.ops import unary_union
# import re

# # SHP 파일 불러오기
# gdf = gpd.read_file("/Users/jeongeunju/Desktop/with-pets/data/LARD_ADM_SECT_SGG_47_202505.shp")

# # 경상북도만 필터링
# gdf = gdf[gdf["SGG_NM"].str.contains("경상북도")].copy()

# # 시군 이름 추출 함수
# def extract_sigun(name):
#     if "포항시" in name:
#         return "포항시"  # 포항시 남구/북구 → 포항시
#     match = re.search(r"경상북도\s+(\S+?[시군])", name)
#     return match.group(1) if match else None

# # '행정구역' 컬럼 만들기
# gdf["행정구역"] = gdf["SGG_NM"].apply(extract_sigun)

# # 유효한 값만 남기기
# gdf = gdf[gdf["행정구역"].notna()].copy()

# # 시군 단위로 그룹화 및 병합
# rows = []
# for name, grouped in gdf.groupby("행정구역"):
#     geom = unary_union(grouped.geometry)
#     rows.append({"행정구역": name, "geometry": geom})

# # GeoDataFrame 생성
# gdf_final = gpd.GeoDataFrame(rows, crs=gdf.crs)




# import geopandas as gpd

# # 원래 GeoJSON 불러오기
# gdf = gpd.read_file("/Users/jeongeunju/Desktop/with-pets/data/gyeongbuk_polygon.geojson")

# # 좌표계를 위도/경도(EPSG:4326)로 변환
# gdf = gdf.to_crs(epsg=4326)

# # 변환된 GeoJSON으로 저장
# gdf.to_file("gyeongbuk_polygon_4326.geojson", driver="GeoJSON")




# import geopandas as gpd

# gdf = gpd.read_file("dashboard/data/gyeongbuk_polygon_4326.geojson")
# print(gdf.columns)



# import folium
# import json
# import os
# from folium import Element

# # --- 경로 설정 ---
# base_dir = os.path.dirname(__file__)
# geojson_path = os.path.join(base_dir, "dashboard/data/gyeongbuk_polygon_4326.geojson")
# output_path = os.path.join(base_dir, "dashboard/www/gyeongbuk_map.html")

# # --- GeoJSON 불러오기 ---
# with open(geojson_path, encoding="utf-8") as f:
#     geojson_data = json.load(f)

# # --- 지도 생성 ---
# m = folium.Map(location=[36.5, 128.8], zoom_start=8, tiles="cartodbpositron")

# # --- 기본 스타일 함수 ---
# def style_function(feature):
#     return {
#         "fillColor": "#a7c8f2",     # 기본 색
#         "color": "black",
#         "weight": 1.5,
#         "fillOpacity": 0.6
#     }

# # --- 마우스 호버 효과 함수 ---
# def highlight_function(feature):
#     return {
#         "fillColor": "#5fa2e0",     # 호버 색 (더 진한 파랑)
#         "color": "black",
#         "weight": 3,                # 테두리 두껍게
#         "fillOpacity": 0.8,
#     }

# # --- GeoJson 레이어 추가 ---
# geojson_layer = folium.GeoJson(
#     geojson_data,
#     name="경북 시군",
#     style_function=style_function,
#     highlight_function=highlight_function,  # ✅ 호버 스타일
#     tooltip=folium.GeoJsonTooltip(fields=["행정구역"], aliases=["지역:"])
# )
# geojson_layer.add_to(m)

# # --- GeoJson 레이어 이름 가져오기 (JS 접근용) ---
# layer_name = geojson_layer.get_name()

# # --- 클릭 이벤트 + 선택 강조 JS 코드 추가 ---
# click_js = f"""
# <script>
# document.addEventListener("DOMContentLoaded", function() {{
#     var layerGroup = {layer_name};
#     var selectedLayer = null;

#     layerGroup.eachLayer(function(layer) {{
#         layer.on("click", function(e) {{
#             var region = layer.feature.properties["행정구역"];
#             console.log("클릭된 지역:", region);

#             // 이전 선택 해제
#             if (selectedLayer) {{
#                 selectedLayer.setStyle({{
#                     fillColor: "#a7c8f2",
#                     weight: 1.5,
#                     fillOpacity: 0.6
#                 }});
#             }}

#             // 현재 선택 스타일 적용
#             layer.setStyle({{
#                 fillColor: "#2166ac",  // 더 진한 파랑
#                 weight: 4,
#                 fillOpacity: 0.95
#             }});

#             selectedLayer = layer;

#             // Shiny에 값 전달
#             if (window.Shiny) {{
#                 Shiny.setInputValue("selected_region", region, {{priority: "event"}});
#             }}
#         }});
#     }});
# }});
# </script>
# """

# # --- JS 코드 삽입 ---
# m.get_root().html.add_child(Element(click_js))

# # --- 저장 ---
# m.save(output_path)
# print(f"지도 저장 완료: {output_path}")




from plots import map

map.generate_interactive_map(
    "dashboard/data/gyeongbuk_polygon_4326.geojson",
    "dashboard/www/gyeongbuk_map.html"
)
