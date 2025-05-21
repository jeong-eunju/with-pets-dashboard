import pandas as pd
import plotly.express as px
from collections import defaultdict

# 고정 인구 수 데이터
REGIONS = [
    "포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", "문경시", "경산시",
    "의성군", "청송군", "영양군", "영덕군", "청도군", "고령군", "성주군", "칠곡군", "예천군", "봉화군",
    "울진군", "울릉군"
]

POPULATION = [
    498296, 257668, 138999, 154788, 410306, 99894, 101185, 93081, 67674, 285618,
    49336, 23867, 15494, 34338, 41641, 32350, 43543, 111928, 54868, 28988,
    47872, 9199
]

def analyze_accident_data(excel_path: str) -> pd.DataFrame:
    df = pd.read_excel(excel_path)
    df = df.loc[df['구분'] == '사고']
    df = df.drop(columns=['연도', '구분']).mean()

    # 이름 매핑
    mapping_dict = {
        '포항북부': '포항시', '포항남부': '포항시', '경주': '경주시', '김천': '김천시',
        '안동': '안동시', '구미': '구미시', '영주': '영주시', '영천': '영천시', '상주': '상주시',
        '문경': '문경시', '경산': '경산시', '의성': '의성군', '청송': '청송군', '영양': '영양군',
        '영덕': '영덕군', '청도': '청도군', '고령': '고령군', '성주': '성주군', '칠곡': '칠곡군',
        '예천': '예천군', '봉화': '봉화군', '울진': '울진군', '울릉': '울릉군'
    }

    # 평균 사고 건수 계산
    city_accident_avg = defaultdict(list)
    for region, value in df.items():
        std_city = mapping_dict.get(region)
        if std_city:
            city_accident_avg[std_city].append(value)

    city_accident_avg = {
        city: sum(values) / len(values) for city, values in city_accident_avg.items()
    }

    acc_df = pd.DataFrame({
        '시군': list(city_accident_avg.keys()),
        '평균사고건수': list(city_accident_avg.values())
    })

    pop_df = pd.DataFrame({'시군': REGIONS, '인구수': POPULATION})
    merged_df = pd.merge(acc_df, pop_df, on='시군')
    merged_df['사고비율'] = merged_df['평균사고건수'] / merged_df['인구수']

    merged_df = merged_df.sort_values("사고비율", ascending=False)
    return merged_df

def plot_accident_data(df: pd.DataFrame, selected_region: str):
    df = df.copy()

    df["color"] = ["highlight" if r == selected_region else "other" for r in df["시군"]]
    df["color"] = pd.Categorical(df["color"], categories=["highlight", "other"])

    fig = px.bar(
        df,
        x="시군",
        y="사고비율",
        color="color",
        color_discrete_map={
            "highlight": "#2ca02c",  # ✅ 초록 강조
            "other": "#dddddd"       # ✅ 연회색 기본
        },
        labels={
            "시군": "",                    # ✅ x축 제목 제거
            "사고비율": "1인당 평균 사고 건수"  # ✅ y축 제목
        },
        category_orders={"시군": df["시군"].tolist()},
        custom_data=["평균사고건수", "인구수"]
    )

    fig.update_layout(
        showlegend=False,              # ✅ 범례 제거
        xaxis=dict(automargin=True,
                   tickangle=-45),  # ✅ 지역명은 유지  
        margin=dict(t=30, b=0),        # ✅ 여백 최소화
        template='plotly_white'
    )

    fig.update_traces(
        hovertemplate='평균 사고 건수: %{customdata[0]}건<br>인구 수: %{customdata[1]}명<br>1인당 사고 건수: %{y:.5f}<extra></extra>'
    )

    return fig
