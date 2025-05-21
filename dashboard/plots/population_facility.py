import pandas as pd
import plotly.express as px
from plots.utils import unify_and_filter_region

def analyze_population_facility_ratio(facility_file_path: str, population_file_path: str) -> pd.DataFrame:
    facility_df = pd.read_csv(facility_file_path, encoding="cp949")

    facility_df = unify_and_filter_region(facility_df, "시도 명칭", "시군구 명칭")


    pop_raw = pd.read_excel(
        population_file_path,
        sheet_name="1-2. 읍면동별 인구 및 세대현황",
        header=[3, 4]
    )
    pop_df = pop_raw[[("구분", "Unnamed: 0_level_1"), ("총계", "총   계")]].copy()
    pop_df.columns = ["region", "population"]

 
    pop_df = unify_and_filter_region(pop_df, "region")

    pop_df = pop_df[pop_df["region"].isin(facility_df["region"].unique())]
    df_fac_cnt = facility_df.groupby("region").size().reset_index(name="facility_count")

    df_merge = pd.merge(df_fac_cnt, pop_df, on="region")
    df_merge["per_person"] = df_merge["facility_count"] / df_merge["population"]
    df_merge = df_merge.sort_values("per_person", ascending=True)

    return df_merge


def plot_population_facility_ratio(df: pd.DataFrame, selected_region: str):
    df = df.copy()

    df["color"] = pd.Categorical(
        ["highlight" if r == selected_region else "other" for r in df["region"]],
        categories=["highlight", "other"]
    )

    fig = px.bar(
        df,
        x="region",
        y="per_person",
        color="color",
        color_discrete_map={
            "highlight": "#2ca02c",  # 강조 색상 (초록)
            "other": "#dddddd"       # 기본 색상 (연회색)
        },
        category_orders={"region": df["region"].tolist()},
        custom_data=["facility_count", "population"],
        labels={
            "region": "",               # ✅ x축 제목 숨김
            "per_person": "1인당 시설 수"  # ✅ y축 제목
        }
    )

    fig.update_layout(
        showlegend=False,              # ✅ 범례 제거
        xaxis=dict(automargin=True,
                   tickangle=-45),  # ✅ 지역명은 유지  
        margin=dict(t=30, b=0),        # ✅ 여백 최소화
        template='plotly_white'
    )


    fig.update_traces(
        hovertemplate='시설 수: %{customdata[0]}개<br>인구 수: %{customdata[1]}명<br>1인당 시설 수: %{y:.6f}<extra></extra>'
    )

    return fig
