import os
import pandas as pd
from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_widget

from plots import map
from plots import crime_rate
from plots import population_facility
from plots import park_area
from plots import traffic
from plots import air_pollution
from plots.radar import plot_radar_chart

# --- Folium 지도 HTML 경로 설정 및 생성 ---
map_html_path = os.path.join(os.getcwd(), "dashboard/www/gyeongbuk_map.html")
geojson_path = os.path.join(os.getcwd(), "dashboard/data/gyeongbuk_polygon_4326.geojson")

if not os.path.exists(map_html_path):
    map.generate_interactive_map(geojson_path, output_path=map_html_path)

# --- 선택된 지역 상태 저장용 변수 ---
selected_region = reactive.Value(None)

# --- UI 구성 ---
app_ui = ui.page_fluid(
    ui.panel_title("반려동물 친화 환경 대시보드"),

    # 메시지 수신 스크립트
    ui.tags.script("""
    document.addEventListener("DOMContentLoaded", function() {
        window.addEventListener("message", function(event) {
            console.log("전달받은 메시지:", event.data);
            if (event.data && typeof event.data === 'string') {
                Shiny.setInputValue("selected_region", event.data, {priority: "event"});
            }
        });
    });
    """),

    ui.div(
        ui.output_text("selected_region_text"),
        style="""
        position: absolute;
        top: 110px;
        right: 680px;
        z-index: 1000;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
    """
    ),

    ui.row(
        ui.column(
            4,
            ui.card(
                ui.card_header("레이더차트"),
                output_widget("plot_radar"),
                style="height: 600px; overflow: hidden;"
            )
        ),
        ui.column(
            4,
            ui.card(
                ui.card_header("클릭 가능한 시군구 지도"),
                ui.tags.iframe(
                    src="gyeongbuk_map.html",
                    width="100%",
                    height="530px",
                    style="border:none;"
                )
            )
        ),
        ui.column(
            4,
            ui.card(
                ui.card_header("경상북도 시군구별 1인당 범죄 건수"),
                output_widget("plot_crime"),
                style="height: 290px; overflow: hidden;"
            ),
            ui.card(
                ui.card_header("경상북도 시군구별 1인당 반려동물 관련 시설 수(μ=10⁻⁶)"),
                output_widget("plot_facility"),
                style="height: 290px; overflow: hidden;"
            )
        )
    ),

    ui.row(
        ui.column(
            4,
            ui.card(
                ui.card_header("경상북도 시군구별 연간 대기오염도"),
                output_widget("plot_air"),
                style="height: 300px; overflow: hidden;"
            )
        ),
        ui.column(
            4,
            ui.card(
                ui.card_header("경상북도 시군구별 1인당 도시공원 면적(㎡)"),
                output_widget("plot_park"),
                style="height: 300px; overflow: hidden;"
            )
        ),
        ui.column(
            4,
            ui.card(
                ui.card_header("경상북도 시군구별 인구 수 대비 교통사고 건수"),
                output_widget("plot_accident"),
                style="height: 300px; overflow: hidden;"
            )
        )
    )
)

# --- 서버 구성 ---
def server(input, output, session):

    @reactive.effect
    @reactive.event(input.selected_region)
    def _():
        selected_region.set(input.selected_region())

    @output
    @render.text
    def selected_region_text():
        region = selected_region()
        if region:
            return f"선택된 지역: {region}"
        else:
            return "보고싶은 지역을 클릭해 주세요."

    @output
    @render_widget
    def plot_radar():
        return plot_radar_chart(
            park_fp="dashboard/data/시군별_공원_면적.xlsx",
            acc_fp="dashboard/data/경상북도 시도별 교통사고 건수.xlsx",
            facility_fp="dashboard/data/한국문화정보원_전국 반려동물 동반 가능 문화시설 위치 데이터_20221130.csv",
            pop_fp="dashboard/data/경상북도 주민등록.xlsx",
            crime_fp="dashboard/data/경찰청_범죄 발생 지역별 통계.xlsx",
            pollution_fp="dashboard/data/월별_도시별_대기오염도.xlsx",
            selected_region=selected_region()
        )

    @output
    @render_widget
    def plot_crime():
        region = selected_region()
        df = crime_rate.analyze_crime_rate(
            "dashboard/data/경찰청_범죄 발생 지역별 통계.xlsx",
            "dashboard/data/경상북도 주민등록.xlsx"
        )
        return crime_rate.plot_crime_rate(df, region)

    @output
    @render_widget
    def plot_facility():
        region = selected_region()
        df = population_facility.analyze_population_facility_ratio(
            "dashboard/data/한국문화정보원_전국 반려동물 동반 가능 문화시설 위치 데이터_20221130.csv",
            "dashboard/data/경상북도 주민등록.xlsx"
        )
        return population_facility.plot_population_facility_ratio(df, region)

    @output
    @render_widget
    def plot_park():
        region = selected_region()
        df = park_area.analyze_park_area("dashboard/data/시군별_공원_면적.xlsx")
        return park_area.plot_park_area(df, region)

    @output
    @render_widget
    def plot_air():
        region = selected_region()
        df = air_pollution.analyze_air_pollution_data("dashboard/data/월별_도시별_대기오염도.xlsx")
        return air_pollution.plot_stacked_bar(df, region)

    @output
    @render_widget
    def plot_accident():
        region = selected_region()
        df = traffic.analyze_accident_data("dashboard/data/경상북도 시도별 교통사고 건수.xlsx")
        return traffic.plot_accident_data(df, region)

# --- 앱 실행 ---
static_path = os.path.join(os.getcwd(), "dashboard/www")
app = App(app_ui, server, static_assets=static_path)
