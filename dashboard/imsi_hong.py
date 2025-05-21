import pandas as pd
import plotly.express as px

# 시군구 컬럼을 region으로 통일하고, 군위군 제거하는 함수
def unify_and_filter_region(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df['region'] = df[col].astype(str).str.split().str[0]
    return df[df['region'] != '군위군']

# ─────────────────────────────────────────────
# 1) 시설 데이터 처리 & 스택형 바 차트
# ─────────────────────────────────────────────
def create_facility_chart(facility_file_path):
    # 시설 데이터 읽기 및 처리
    df_fac = pd.read_csv(
        facility_file_path,
        encoding="cp949"
    )
    df_fac = df_fac[df_fac["시도 명칭"] == "경상북도"]
    df_fac = unify_and_filter_region(df_fac, "시군구 명칭")
    
    # 카테고리별 그룹화
    df_fac_cnt2 = (
        df_fac
        .groupby(["region", "카테고리2"])
        .size()
        .reset_index(name="count")
    )
    
    # 총합 계산 및 정렬
    totals = (
        df_fac_cnt2
        .groupby("region")["count"]
        .sum()
        .reset_index(name="total")
        .sort_values("total", ascending=False)
    )
    order = totals["region"].tolist()
    
    # 그래프 생성
    fig = px.bar(
        df_fac_cnt2,
        x="region",
        y="count",
        color="카테고리2",
        category_orders={"region": order},
        barmode="stack",
        labels={"region":"시군구", "count":"시설 수", "카테고리2":"유형"},
        title="경북 시군구별 시설 유형 분포 (스택형)",
        width=900,
        height=600
    )
    
    # 영천시 강조
    y영 = totals.loc[totals.region=="영천시", "total"].iloc[0]
    fig.add_annotation(
        x="영천시", y=y영+5, text="영천시",
        showarrow=True, arrowhead=1, arrowwidth=4,
        ax=0, ay=-50, font=dict(color="green"), arrowcolor="green"
    )
    
    # 레이아웃 설정
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=True,
        margin=dict(b=100)
    )
    
    # 호버 템플릿 수정 - 시군구 제외, 유형과 시설 수만 표시
    fig.update_traces(
        hovertemplate='유형: %{customdata}<br>시설 수: %{y}<extra></extra>'
    )
    # customdata 설정으로 hover에 카테고리2 표시
    for i, trace in enumerate(fig.data):
        category = trace.name
        fig.data[i].customdata = [category] * len(trace.x)
    
    return fig, df_fac

# ─────────────────────────────────────────────
# 2) 등록 동물 수 대비 시설 수 차트
# ─────────────────────────────────────────────
def create_animal_facility_chart(facility_data, animal_file_path):
    # 동물 등록 데이터 읽기 및 처리
    df_reg = pd.read_csv(
        animal_file_path,
        encoding="cp949"
    )
    df_reg = df_reg[df_reg["시도"] == "경상북도"].dropna(subset=["시군구"])
    df_reg = unify_and_filter_region(df_reg, "시군구")
    df_reg_sum = (
        df_reg
        .groupby("region", as_index=False)["총 등록 누계"]
        .sum()
        .rename(columns={"총 등록 누계":"registered"})
    )
    
    # 시설 데이터와 병합
    df_merge = pd.merge(
        facility_data.groupby("region").size().reset_index(name="facility_count"),
        df_reg_sum,
        on="region"
    )
    
    # 1마리당 시설 수 계산 및 정렬
    df_merge["per_animal"] = df_merge["facility_count"] / df_merge["registered"]
    df_merge = df_merge.sort_values("per_animal", ascending=False)
    df_merge["color"] = df_merge["region"].map(lambda r: "영천시" if r=="영천시" else "기타")
    
    # 그래프 생성
    fig = px.bar(
        df_merge,
        x="region",
        y="per_animal",
        color="color",
        color_discrete_map={"영천시":"green","기타":"lightgreen"},
        labels={"region":"시군구", "per_animal":"시설 수 (1마리당)"},
        title="경상북도 시군구별 등록 동물 1마리당 시설 수",
        category_orders={"region": df_merge["region"].tolist()},
        width=800,
        height=500,
        custom_data=["facility_count", "registered"]  # 호버에 추가 정보 표시를 위한 custom_data
    )
    
    # 레이아웃 설정
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(b=100),
        yaxis=dict(tickformat='.5f')
    )
    
    # 호버 템플릿 수정 - 시설수, 등록 동물수, 1마리당 시설수 표시
    fig.update_traces(
        hovertemplate='시설 수: %{customdata[0]}<br>등록 동물 수: %{customdata[1]}<br>동물 1마리당 시설 수: %{y:.5f}<extra></extra>'
    )
    
    return fig

# ─────────────────────────────────────────────
# 3) 인구 대비 시설 수 차트
# ─────────────────────────────────────────────
def create_population_facility_chart(facility_data, population_file_path):
    # 인구 데이터 읽기 및 처리
    pop_raw = pd.read_excel(
        population_file_path,
        sheet_name="1-2. 읍면동별 인구 및 세대현황",
        header=[3,4]
    )
    pop_df = pop_raw[[("구분","Unnamed: 0_level_1"),("총계","총   계")]].copy()
    pop_df.columns = ["region","population"]
    pop_df = unify_and_filter_region(pop_df, "region")
    pop_df = pop_df[pop_df["region"].isin(facility_data.groupby("region").size().index)]
    
    # 시설 데이터와 병합
    df_merge = pd.merge(
        facility_data.groupby("region").size().reset_index(name="facility_count"),
        pop_df,
        on="region"
    )
    
    # 1인당 시설 수 계산 및 정렬
    df_merge["per_person"] = df_merge["facility_count"] / df_merge["population"]
    df_merge = df_merge.sort_values("per_person", ascending=False)
    df_merge["color"] = df_merge["region"].map(lambda r: "영천시" if r=="영천시" else "기타")
    
    # 그래프 생성
    fig = px.bar(
        df_merge,
        x="region",
        y="per_person",
        color="color",
        color_discrete_map={"영천시":"green","기타":"lightgreen"},
        labels={"region":"시군구", "per_person":"시설 수 (1인당)"},
        title="경상북도 시군구별 1인당 시설 수",
        category_orders={"region": df_merge["region"].tolist()},
        width=800,
        height=500,
        custom_data=["facility_count", "population"]  # 호버에 추가 정보 표시를 위한 custom_data
    )
    
    # 레이아웃 설정
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(b=100),
        yaxis=dict(tickformat='.6f')
    )
    
    # 호버 템플릿 수정 - 시설수, 인구수, 1인당 시설수 표시
    fig.update_traces(
        hovertemplate='시설 수: %{customdata[0]}<br>인구 수: %{customdata[1]}<br>1인당 시설 수: %{y:.6f}<extra></extra>'
    )
    
    return fig

# ─────────────────────────────────────────────
# 메인 코드 실행
# ─────────────────────────────────────────────
# 파일 경로 설정
facility_file_path = "./data/한국문화정보원_전국 반려동물 동반 가능 문화시설 위치 데이터_20221130.csv"
animal_file_path = "./data/농림축산식품부 농림축산검역본부_행정구역별 반려동물등록 개체 수 현황_20221231.csv"
population_file_path = "./data/경상북도 주민등록.xlsx"

# 1) 시설 유형 분포 차트 생성 및 표시
fig1, df_fac = create_facility_chart(facility_file_path)
fig1.show()

# 2) 동물 1마리당 시설 수 차트 생성 및 표시
fig2 = create_animal_facility_chart(df_fac, animal_file_path)
fig2.show()

# 3) 1인당 시설 수 차트 생성 및 표시
fig3 = create_population_facility_chart(df_fac, population_file_path)
fig3.show()

''''''''''''''''''''''''''''''''''''
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio

# 파일 읽기
def analyze_air_pollution_data(file_path):
    # 엑셀 파일의 모든 시트를 읽어오기
    pollutants = {
        'PM2.5': '미세먼지_PM2.5__월별_도시별_대기오염도',
        'PM10': '미세먼지_PM10__월별_도시별_대기오염도',
        'O3': '오존_월별_도시별_대기오염도',
        'CO': '일산화탄소_월별_도시별_대기오염도',
        'NO2': '이산화질소_월별_도시별_대기오염도'
    }
    
    # 모든 오염물질에 대한 데이터프레임 저장
    dfs = {}
    for pollutant, sheet_name in pollutants.items():
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            dfs[pollutant] = df
        except Exception as e:
            print(f"{pollutant} 데이터 로드 중 오류: {e}")
    
    # 경상북도 시군구별 연간 평균값 계산
    results = {}
    
    for pollutant, df in dfs.items():
        # 경상북도 데이터만 필터링 ('구분(1)' 컬럼이 '경상북도'인 행 선택)
        gyeongbuk_df = df[df['구분(1)'] == '경상북도']
        
        # 월별 데이터 컬럼 선택 (연도.월 형식의 컬럼들, '구분(1)', '구분(2)' 제외)
        month_columns = [col for col in df.columns if str(col).replace('.', '').isdigit()]
        
        # 시군구별 평균 계산
        gyeongbuk_avg = gyeongbuk_df.groupby('구분(2)')[month_columns].mean().mean(axis=1).reset_index()
        gyeongbuk_avg.columns = ['시군구', f'{pollutant}_평균']
        
        # 결과 저장
        if 'result_df' not in results:
            results['result_df'] = gyeongbuk_avg
        else:
            results['result_df'] = pd.merge(results['result_df'], gyeongbuk_avg, on='시군구', how='outer')
    
    return results['result_df']

# Plotly를 사용한 스택형 막대그래프 그리기
def plot_stacked_bar_plotly(data):
    # 데이터 준비
    pollutant_cols = [col for col in data.columns if col != '시군구']
    
    # 총합 계산하여 오름차순 정렬
    data['총합'] = data[pollutant_cols].sum(axis=1)
    data_sorted = data.sort_values(by='총합', ascending=True)
    
    # 그래프 생성
    fig = go.Figure()
    
    # 스택형 막대그래프 데이터 추가
    for col in pollutant_cols:
        pollutant_name = col.split('_')[0]  # 'PM2.5_평균'에서 'PM2.5' 추출
        fig.add_trace(go.Bar(
            x=data_sorted['시군구'],
            y=data_sorted[col],
            name=pollutant_name,
            hovertemplate=f'{pollutant_name} 대기오염도: %{{y:.2f}}<extra></extra>',
        ))
    
    # 스택 모드로 설정
    fig.update_layout(
        barmode='stack',
        title='경상북도 시군구별 연간 대기오염도 평균',
        xaxis={'title': '시군구', 'tickangle': -45},
        yaxis={'title': '오염물질 농도'},
        legend_title='오염물질',
        height=600,
        width=1000,
        hovermode='closest',
        template='plotly_white'
    )
    
    # 영천시에 화살표 추가
    if '영천시' in data_sorted['시군구'].values:
        # 영천시의 총합 값을 구함
        y_yeongcheon = data_sorted.loc[data_sorted['시군구'] == '영천시', '총합'].iloc[0]
        
        # 화살표 주석 추가
        fig.add_annotation(
            x='영천시', 
            y=y_yeongcheon + 2,  # 막대 위에 표시
            text="영천시",
            showarrow=True, 
            arrowhead=1, 
            arrowwidth=4,
            ax=0, 
            ay=-50, 
            font=dict(color="green"),
            arrowcolor="green"
        )
    
    return fig

# 메인 함수
def main():
    file_path = './data/월별_도시별_대기오염도.xlsx'
    
    # 데이터 분석
    result_df = analyze_air_pollution_data(file_path)

    # Plotly로 데이터 시각화
    fig = plot_stacked_bar_plotly(result_df)
    
    # 그래프 표시
    fig.show()


main()


''''''''''''''''''''''''''''''''''''''''''''''''
import pandas as pd
import plotly.express as px

def analyze_crime_data(file_path):
    # 엑셀 파일 읽기
    df = pd.read_excel(file_path)
    
    # 범죄대분류, 범죄중분류를 제외한 모든 열(시군구)을 선택
    region_columns = [col for col in df.columns if col not in ['범죄대분류', '범죄중분류']]
    
    # 각 시군구별 총 범죄건수 계산
    total_crimes = df[region_columns].sum()
    
    # 데이터프레임으로 변환하고 오름차순 정렬
    result_df = total_crimes.reset_index()
    result_df.columns = ['시군구', '총범죄건수']
    result_df = result_df.sort_values(by='총범죄건수', ascending=True)
    
    # 영천시와 다른 시군구 구분을 위한 색상 컬럼 추가
    result_df['color'] = result_df['시군구'].map(lambda r: "영천시" if r == "영천시" else "기타")
    
    return result_df

def plot_crime_bar_chart(data):
    # 오름차순 정렬된 순서 유지를 위한 목록
    ordered_regions = data['시군구'].tolist()
    
    # 오름차순 정렬된 데이터로 막대그래프 생성 (색상 구분 적용)
    fig = px.bar(
        data,
        x='시군구',
        y='총범죄건수',
        color='color',  # 색상 구분에 사용할 컬럼
        color_discrete_map={"영천시": "green", "기타": "lightgreen"},  # 색상 매핑
        category_orders={"시군구": ordered_regions},  # 정렬 순서 유지
        title='경상북도 시군구별 총 범죄 발생 건수',
        labels={'시군구': '시군구', '총범죄건수': '총 범죄 건수'},
    )
    
    # 그래프 레이아웃 설정
    fig.update_layout(
        xaxis_tickangle=-45,  # x축 레이블 각도
        xaxis_title='시군구',
        yaxis_title='총 범죄 건수',
        height=600,
        width=1000,
        template='plotly_white',
        showlegend=False,  # 범례 제거
        margin=dict(b=100)  # 하단 여백 추가
    )
    
    # 호버 템플릿 수정 - 총 범죄 건수만 표시
    fig.update_traces(
        hovertemplate='범죄 건수: %{y}<extra></extra>'
    )
    
    return fig

def main():
    file_path = './data/경찰청_범죄 발생 지역별 통계.xlsx'
    
    # 데이터 분석
    result_df = analyze_crime_data(file_path)
    
    # 막대그래프 생성
    fig = plot_crime_bar_chart(result_df)
    
    # 그래프 표시
    fig.show()

main()



''''''''''''''''''''''''''''''''''''
import pandas as pd
import plotly.express as px
import numpy as np

# 시군구 컬럼을 region으로 통일하고, 군위군 제거하는 함수
def unify_and_filter_region(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df['region'] = df[col].astype(str).str.split().str[0]
    return df[df['region'] != '군위군']

def analyze_crime_rate(crime_file_path, population_file_path):
    # 1. 범죄 데이터 처리
    # 범죄 엑셀 파일 읽기
    crime_df = pd.read_excel(crime_file_path)
    
    # 범죄대분류, 범죄중분류를 제외한 모든 열(시군구)을 선택
    region_columns = [col for col in crime_df.columns if col not in ['범죄대분류', '범죄중분류']]
    
    # 각 시군구별 총 범죄건수 계산
    total_crimes = crime_df[region_columns].sum().reset_index()
    total_crimes.columns = ['시군구', '총범죄건수']
    
    # 2. 인구 데이터 처리
    # 인구 엑셀 파일 읽기
    pop_raw = pd.read_excel(
        population_file_path,
        sheet_name="1-2. 읍면동별 인구 및 세대현황",
        header=[3,4]
    )
    
    # 필요한 컬럼만 선택 (구분과 총계)
    pop_df = pop_raw[[("구분","Unnamed: 0_level_1"),("총계","총   계")]].copy()
    pop_df.columns = ["region", "population"]
    
    # 지역명 정리
    pop_df = unify_and_filter_region(pop_df, "region")
    
    # 3. 데이터 합치기
    # 범죄 데이터 지역명 표준화 (총범죄건수 데이터프레임의 시군구 컬럼을 region으로 변환)
    crime_data = total_crimes.copy()
    crime_data['region'] = crime_data['시군구']
    
    # 범죄 데이터와 인구 데이터 합치기
    merged_data = pd.merge(
        crime_data[['region', '총범죄건수']],
        pop_df,
        on="region",
        how="inner"  # 두 데이터에 모두 있는 지역만 사용
    )
    
    # 4. 범죄율 계산 (1인당 범죄 건수)
    merged_data["범죄율"] = merged_data["총범죄건수"] / merged_data["population"]
    
    # 5. 오름차순 정렬 및 색상 지정
    merged_data = merged_data.sort_values("범죄율", ascending=True)
    merged_data["color"] = merged_data["region"].map(lambda r: "영천시" if r=="영천시" else "기타")
    
    return merged_data

def plot_crime_rate(data):
    # 오름차순 정렬된 순서 유지
    ordered_regions = data['region'].tolist()
    
    # 그래프 생성
    fig = px.bar(
        data,
        x="region",
        y="범죄율",
        color="color",
        color_discrete_map={"영천시":"green","기타":"lightgreen"},
        labels={"region":"시군구", "범죄율":"1인당 범죄 건수"},
        title="경상북도 시군구별 1인당 범죄 건수",
        category_orders={"region": ordered_regions},
        width=800,
        height=500,
        custom_data=["총범죄건수", "population"]  # 호버에 추가 정보 표시를 위한 custom_data
    )
    
    # 그래프 레이아웃 설정
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(b=100),
        yaxis=dict(
            tickformat='.5f'
        )
    )
    
    # 호버 템플릿 수정 - 범죄수, 인구수, 1인당 범죄 건수 표시
    fig.update_traces(
        hovertemplate='범죄 건수: %{customdata[0]}<br>인구 수: %{customdata[1]}<br>1인당 범죄 건수: %{y:.5f}<extra></extra>'
    )
    
    return fig

def main():
    crime_file_path = './data/경찰청_범죄 발생 지역별 통계.xlsx'
    population_file_path = './data/경상북도 주민등록.xlsx'
    
    # 데이터 분석
    result_df = analyze_crime_rate(crime_file_path, population_file_path)
    
    # 막대그래프 생성
    fig = plot_crime_rate(result_df)
    
    # 그래프 표시
    fig.show()

main()



import pandas as pd
from plots import facility_stacked

facility_file_path = "/Users/jeongeunju/Desktop/with-pets/dashboard/data/한국문화정보원_전국 반려동물 동반 가능 문화시설 위치 데이터_20221130.csv"
facility_df = pd.read_csv(facility_file_path, encoding="cp949")

fig = facility_stacked.plot(None, facility_df)
fig.show()
