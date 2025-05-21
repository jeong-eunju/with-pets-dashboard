import pandas as pd
import plotly.express as px
from plots.utils import unify_and_filter_region

def analyze_crime_rate(crime_file_path, population_file_path):
    crime_df = pd.read_excel(crime_file_path)
    region_columns = [col for col in crime_df.columns if col not in ['범죄대분류', '범죄중분류']]
    total_crimes = crime_df[region_columns].sum().reset_index()
    total_crimes.columns = ['시군구', '총범죄건수']

    pop_raw = pd.read_excel(population_file_path, sheet_name="1-2. 읍면동별 인구 및 세대현황", header=[3,4])
    pop_df = pop_raw[[("구분","Unnamed: 0_level_1"),("총계","총   계")]].copy()
    pop_df.columns = ["region", "population"]
    pop_df = unify_and_filter_region(pop_df, "region")

    crime_data = total_crimes.copy()
    crime_data['region'] = crime_data['시군구']

    merged = pd.merge(
        crime_data[['region', '총범죄건수']],
        pop_df,
        on="region",
        how="inner"
    )
    merged["범죄율"] = merged["총범죄건수"] / merged["population"]
    merged = merged.sort_values("범죄율", ascending=False)
    return merged

def plot_crime_rate(df, selected_region):
    df = df.copy()

    df["color"] = pd.Categorical(
        ["highlight" if r == selected_region else "other" for r in df["region"]],
        categories=["highlight", "other"]
    )

    fig = px.bar(
        df,
        x="region",
        y="범죄율",
        color="color",
        color_discrete_map={
            "highlight": "#2ca02c",
            "other": "#dddddd"
        },
        category_orders={"region": df["region"].tolist()},
        custom_data=["총범죄건수", "population"],
        labels={
            "region": "",     # ✅ x축 제목 숨김
            "범죄율": "1인당 범죄율"  # y축 제목은 필요하면 유지
        }
    )

    fig.update_layout(
        showlegend=False,  # ✅ 범례 제거
        xaxis=dict(automargin=True,
                   tickangle=-45),  # ✅ 지역명은 유지
        margin=dict(t=30, b=0),        # ✅ 여백 최소화
        template='plotly_white'
    )





    fig.update_traces(
        hovertemplate='범죄 건수: %{customdata[0]}건<br>인구 수: %{customdata[1]}명<br>1인당 범죄 건수: %{y:.5f}<extra></extra>'
    )

    return fig
