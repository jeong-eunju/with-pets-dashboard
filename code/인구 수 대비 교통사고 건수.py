from shiny import App, Inputs, Outputs, Session, ui
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px
from collections import defaultdict

# 엑셀 데이터 경로
EXCEL_PATH = 'C:/Users/LS/Desktop/프로젝트/경상북도 시도별 교통사고 건수.xlsx'

# 시군구 목록 및 인구수
regions = [
    "포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", "문경시", "경산시",
    "의성군", "청송군", "영양군", "영덕군", "청도군", "고령군", "성주군", "칠곡군", "예천군", "봉화군",
    "울진군", "울릉군"
]

population = [
    498296, 257668, 138999, 154788, 410306, 99894, 101185, 93081, 67674, 285618,
    49336, 23867, 15494, 34338, 41641, 32350, 43543, 111928, 54868, 28988,
    47872, 9199
]

# 데이터 준비 함수
def load_accident_data():
    # 엑셀 데이터 불러오기
    df = pd.read_excel(EXCEL_PATH)
    df = df.loc[df['구분'] == '사고']
    df = df.drop(columns=['연도', '구분']).mean()

    # 매핑
    mapping_dict = {
        '포항북부': '포항시', '포항남부': '포항시', '경주': '경주시', '김천': '김천시',
        '안동': '안동시', '구미': '구미시', '영주': '영주시', '영천': '영천시', '상주': '상주시',
        '문경': '문경시', '경산': '경산시', '의성': '의성군', '청송': '청송군', '영양': '영양군',
        '영덕': '영덕군', '청도': '청도군', '고령': '고령군', '성주': '성주군', '칠곡': '칠곡군',
        '예천': '예천군', '봉화': '봉화군', '울진': '울진군', '울릉': '울릉군'
    }

    # 사고 평균 데이터
    city_accident_avg = defaultdict(list)
    for region, value in df.items():
        std_city = mapping_dict.get(region)
        if std_city:
            city_accident_avg[std_city].append(value)
    city_accident_avg = {city: sum(values)/len(values) for city, values in city_accident_avg.items()}

    acc_df = pd.DataFrame({
        '시군': list(city_accident_avg.keys()),
        '평균사고건수': list(city_accident_avg.values())
    })

    # 인구수 데이터프레임 생성
    pop_df = pd.DataFrame({'시군': regions, '인구수': population})

    # 병합 및 계산
    merged_df = pd.merge(acc_df, pop_df, on='시군')
    merged_df['인구 수 대비 평균사고건수'] = merged_df['평균사고건수'] / merged_df['인구수']
    return merged_df

# 시각화 함수
def create_plot(highlight_region="영천시"):
    df = load_accident_data()
    df['color'] = df['시군'].apply(lambda x: highlight_region if x == highlight_region else '기타')
    df = df.sort_values(by='인구 수 대비 평균사고건수', ascending=False)

    fig = px.bar(
        df,
        x='시군',
        y='인구 수 대비 평균사고건수',
        color='color',
        hover_data={'color': False},
        color_discrete_map={
            highlight_region: 'green',
            '기타': 'lightgreen'
        },
        title='시군별 인구 수 대비 평균사고건수',
        labels={'시군': '시군', '인구 수 대비 평균사고건수': '평균 사고건수'},
        category_orders={'시군': df['시군'].tolist()},
        height=500,
        width=900
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=40, r=40, t=60, b=120),
        showlegend=False,
        yaxis_tickformat=','
    )

    return fig

# UI 정의
app_ui = ui.page_fluid(
    ui.h2("시군별 인구 수 대비 교통사고 건수 시각화"),
    ui.input_select("highlight", "강조할 시군 선택:", choices=regions, selected="영천시"),
    output_widget("accident_plot")
)

# 서버 정의
def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render_widget
    def accident_plot():
        return create_plot(highlight_region=input.highlight())

# 앱 정의
app = App(app_ui, server)
