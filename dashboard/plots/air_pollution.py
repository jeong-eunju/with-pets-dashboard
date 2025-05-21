import pandas as pd
import numpy as np
import plotly.graph_objects as go

def analyze_air_pollution_data(file_path: str) -> pd.DataFrame:
    pollutants = {
        'PM2.5': '미세먼지_PM2.5__월별_도시별_대기오염도',
        'PM10': '미세먼지_PM10__월별_도시별_대기오염도',
        'O3': '오존_월별_도시별_대기오염도',
        'CO': '일산화탄소_월별_도시별_대기오염도',
        'NO2': '이산화질소_월별_도시별_대기오염도'
    }
    
    result_df = None

    for pollutant, sheet_name in pollutants.items():
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            gyeongbuk_df = df[df['구분(1)'] == '경상북도']
            month_cols = [col for col in df.columns if str(col).replace('.', '').isdigit()]
            avg_df = gyeongbuk_df.groupby('구분(2)')[month_cols].mean().mean(axis=1).reset_index()
            avg_df.columns = ['시군구', f'{pollutant}_평균']
            
            if result_df is None:
                result_df = avg_df
            else:
                result_df = pd.merge(result_df, avg_df, on='시군구', how='outer')
        except Exception as e:
            print(f"{pollutant} 시트 오류: {e}")
    
    return result_df

def plot_stacked_bar(df: pd.DataFrame, selected_region: str = "영천시") -> go.Figure:
    pollutant_cols = [col for col in df.columns if col != '시군구']

    # 정규화
    normalized = df.copy()
    for col in pollutant_cols:
        max_val = normalized[col].max()
        if max_val > 0:
            normalized[col] = normalized[col] / max_val

    normalized['총합'] = normalized[pollutant_cols].sum(axis=1)
    sorted_data = normalized.sort_values('총합', ascending=False)
    original_data = df.set_index('시군구').loc[sorted_data['시군구']].reset_index()

    fig = go.Figure()

    for col in pollutant_cols:
        pollutant_name = col.split('_')[0]
        hover_data = np.stack((
            original_data[col],
            sorted_data[col],
            sorted_data['총합']
        ), axis=-1)

        hover_template = (
            f'<b>{pollutant_name}</b><br>' +
            f'시군구: %{{x}}<br>' +
            f'원본 수치: %{{customdata[0]:.3f}}<br>' +
            f'정규화 수치: %{{customdata[1]:.3f}}<br>' +
            f'5개 물질 총합: %{{customdata[2]:.3f}}<extra></extra>'
        )

        opacity_list = [
            1.0 if region == selected_region else 0.3
            for region in sorted_data['시군구']
        ]

        fig.add_trace(go.Bar(
            x=sorted_data['시군구'],
            y=sorted_data[col],
            name=pollutant_name,
            customdata=hover_data,
            hovertemplate=hover_template,
            marker=dict(opacity=opacity_list)
        ))

    # 🚨 핵심: 막대 수에 맞춰 그래프 전체 너비 줄이기
    num_regions = len(sorted_data)
    fig.update_layout(
        barmode='stack',
        showlegend=True,
        height=240,
        width=580,  # ✅ 카드 하나에 맞는 너비 (column 4 기준)
        margin=dict(t=10, b=10, l=10, r=10),
        bargap=0.15,  # ✅ 막대 사이 간격 조금 줘서 적당한 밀도
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=12),  # ✅ 글자 작게 (안겹침 + 잘 보임)
            automargin=True,
            tickmode='linear'
            
        ),
        yaxis=dict(
            title='정규화 수치',
            tickformat=".2f",
            tickfont=dict(size=9)
        ),
        legend=dict(
            orientation="h",
            x=0.4,
            xanchor="center",
            y=-0.5,
            yanchor="bottom",
            font=dict(size=10)
        ),
        template='plotly_white'
    )


    return fig

