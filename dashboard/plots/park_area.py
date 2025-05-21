import pandas as pd
import plotly.express as px

def analyze_park_area(excel_path: str) -> pd.DataFrame:
    # 공원 면적 데이터
    df = pd.read_excel(excel_path)
    df_subset = df.iloc[3:, [1, 3]]
    df_subset.columns = ['시군', '면적']

    # 시군별 인구 수
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
    merged_df = pd.merge(df_subset, pop_df, on='시군')

    merged_df['면적'] = pd.to_numeric(merged_df['면적'], errors='coerce')
    merged_df['인구수'] = pd.to_numeric(merged_df['인구수'], errors='coerce')

    merged_df['공원면적비율'] = merged_df['면적'] / merged_df['인구수']
    merged_df = merged_df.sort_values("공원면적비율", ascending=True)

    return merged_df

def plot_park_area(df: pd.DataFrame, selected_region: str):
    df["color"] = ["highlight" if r == selected_region else "other" for r in df["시군"]]
    df["color"] = pd.Categorical(df["color"], categories=["highlight", "other"])

    fig = px.bar(
        df,
        x="시군",
        y="공원면적비율",
        color="color",
        color_discrete_map={
            "highlight": "#2ca02c",  # ✅ 강조 색상 (초록)
            "other": "#dddddd"       # ✅ 기본 색상 (연회색)
        },
        labels={
            "시군": "",                  # ✅ x축 제목 숨김
            "공원면적비율": "1인당 도시공원 면적"  # ✅ y축 제목
        },
        category_orders={"시군": df["시군"].tolist()},
        custom_data=["면적", "인구수"]
    )

    fig.update_layout(
        showlegend=False,              # ✅ 범례 제거
        xaxis=dict(automargin=True,
                   tickangle=-45),  # ✅ 지역명은 유지 
        margin=dict(t=30, b=0),        # ✅ 여백 최소화
        template='plotly_white'
    )

    fig.update_traces(
        hovertemplate='공원 총면적: %{customdata[0]}㎡<br>인구 수: %{customdata[1]}명<br>1인당 공원 면적: %{y:.2f}㎡<extra></extra>'
    )

    return fig
