from shiny import App, Inputs, Outputs, Session, ui
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px

# 엑셀 데이터 경로
EXCEL_PATH = "C:/Users/LS/Desktop/프로젝트/시군별_공원_면적.xlsx"

# 데이터 로드 및 전처리
def load_and_prepare_data():
    # 엑셀 데이터 불러오기
    df = pd.read_excel(EXCEL_PATH)

    # 필요한 행과 열 선택
    df_subset = df.iloc[3:, [1, 3]]
    df_subset.columns = ['시군', '면적']

    # 시군구별 인구수 데이터
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

    pop_df = pd.DataFrame({'시군': regions, '인구수': population})

    # 병합
    merged_df = pd.merge(df_subset, pop_df, on='시군')

    # 숫자형으로 변환
    merged_df['면적'] = pd.to_numeric(merged_df['면적'], errors='coerce')
    merged_df['인구수'] = pd.to_numeric(merged_df['인구수'], errors='coerce')

    # 인구 수 대비 면적 계산
    merged_df['인구 수 대비 도시공원 면적'] = round((merged_df['면적']) / merged_df['인구수'], 2)

    return merged_df

# 동적으로 그래프 생성
def create_plot(highlight_region="영천시"):
    df = load_and_prepare_data()
    df['color'] = df['시군'].apply(lambda x: highlight_region if x == highlight_region else '기타')
    df = df.sort_values(by='인구 수 대비 도시공원 면적', ascending=False)

    fig = px.bar(
        df,
        x='시군',
        y='인구 수 대비 도시공원 면적',
        color='color',
        hover_data={'color': False},
        color_discrete_map={
            highlight_region: 'green',
            '기타': 'lightgreen'
        },
        title='인구 수 대비 도시공원 면적',
        labels={'시군': '시군', '인구 수 대비 도시공원 면적': '도시공원 면적 (m²)'},
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
    ui.h2("인구 수 대비 도시공원 면적 시각화"),
    ui.input_select("highlight", "강조할 시군 선택:", choices=[
        "포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", "문경시", "경산시",
        "의성군", "청송군", "영양군", "영덕군", "청도군", "고령군", "성주군", "칠곡군", "예천군", "봉화군",
        "울진군", "울릉군"    ], selected="영천시"),
    output_widget("park_plot")
)

# 서버 정의
def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render_widget
    def park_plot():
        return create_plot(highlight_region=input.highlight())

# 앱 정의
app = App(app_ui, server)
