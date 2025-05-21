import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ─── 인구 데이터 ─────────────────────────────────────────────────
regions = ["포항시","경주시","김천시","안동시","구미시","영주시","영천시","상주시","문경시","경산시",
           "의성군","청송군","영양군","영덕군","청도군","고령군","성주군","칠곡군","예천군","봉화군",
           "울진군","울릉군"]
pop_counts = [498296,257668,138999,154788,410306,99894,101185,93081,67674,285618,
              49336,23867,15494,34338,41641,32350,43543,111928,54868,28988,
              47872,9199]
pop_df = pd.DataFrame({'시군': regions, '인구수': pop_counts})

# ─── 분석 + 시각화 통합 함수 ─────────────────────────────────────────
def plot_radar_chart(park_fp, acc_fp, facility_fp, pop_fp, crime_fp, pollution_fp, selected_region=None):
    # ─── 1) 도시공원 면적 per person ───────────────────────────────────────
    df_park = pd.read_excel(park_fp).iloc[3:,[1,3]]
    df_park.columns = ['시군','면적']
    df_park['면적'] = pd.to_numeric(df_park['면적'],errors='coerce')
    df_park = df_park.merge(pop_df, on='시군')
    df_park['per_person'] = df_park['면적'] / df_park['인구수']  # 1인당 면적 계산
    df_park['park_norm'] = df_park['per_person'] / df_park['per_person'].max()  # 정규화

    # --- 2) 교통사고 ---
    df_acc = pd.read_excel(acc_fp)
    df_acc = df_acc[df_acc['구분'] == '사고'].drop(columns=['연도','구분'])
    acc_mean = df_acc.mean()
    mapping_acc = {
        '포항북부':'포항시','포항남부':'포항시','경주':'경주시','김천':'김천시','안동':'안동시','구미':'구미시','영주':'영주시','영천':'영천시','상주':'상주시',
        '문경':'문경시','경산':'경산시','의성':'의성군','청송':'청송군','영양':'영양군','영덕':'영덕군','청도':'청도군','고령':'고령군',
        '성주':'성주군','칠곡':'칠곡군','예천':'예천군','봉화':'봉화군','울진':'울진군','울릉':'울릉군'
    }
    acc_dict = {}
    for k, v in acc_mean.items():
        city = mapping_acc.get(k)
        if city:
            acc_dict.setdefault(city, []).append(v)
    acc_avg = {city: np.mean(vals) for city, vals in acc_dict.items()}
    df_acc2 = pd.DataFrame.from_dict(acc_avg, orient='index', columns=['acc']).reset_index().rename(columns={'index': '시군'})
    df_acc2 = df_acc2.merge(pop_df, on='시군')
    df_acc2['acc_inv'] = 1 / (df_acc2['acc'] / df_acc2['인구수'])
    df_acc2['acc_norm'] = df_acc2['acc_inv'] / df_acc2['acc_inv'].max()

    # --- 3) 반려동물 시설 ---
    df_fac = pd.read_csv(facility_fp, encoding='cp949')
    df_fac = df_fac[df_fac['시도 명칭'] == '경상북도']
    df_fac['시군'] = df_fac['시군구 명칭'].str.extract(r'^(.*?[시군])')[0]
    df_fac = df_fac[df_fac['시군'] != '군위군']
    fac_counts = df_fac['시군'].value_counts().rename_axis('시군').reset_index(name='facility_count')
    fac_df = fac_counts.merge(pop_df, on='시군')
    fac_df['per_person'] = fac_df['facility_count'] / fac_df['인구수']
    fac_df['fac_norm'] = fac_df['per_person'] / fac_df['per_person'].max()

    # --- 4) 범죄 ---
    crime_df = pd.read_excel(crime_fp)
    cols = [c for c in crime_df.columns if c not in ['범죄대분류', '범죄중분류']]
    crime_tot = crime_df[cols].sum().reset_index()
    crime_tot.columns = ['raw', 'crime']
    crime_tot['시군'] = crime_tot['raw'].str.split().str[0]
    crime_tot = crime_tot[crime_tot['시군'] != '군위군'][['시군', 'crime']]
    crime_tot = crime_tot.merge(pop_df, on='시군')
    crime_tot['crime_inv'] = 1 / (crime_tot['crime'] / crime_tot['인구수'])
    crime_tot['crime_norm'] = crime_tot['crime_inv'] / crime_tot['crime_inv'].max()

    # --- 5) 대기오염 ---
    pollutants = {
        'PM2.5': '미세먼지_PM2.5__월별_도시별_대기오염도',
        'PM10': '미세먼지_PM10__월별_도시별_대기오염도',
        'O3': '오존_월별_도시별_대기오염도',
        'CO': '일산화탄소_월별_도시별_대기오염도',
        'NO2': '이산화질소_월별_도시별_대기오염도'
    }
    polls = []
    for pol, sheet in pollutants.items():
        dfp = pd.read_excel(pollution_fp, sheet_name=sheet)
        dfp = dfp[dfp['구분(1)'] == '경상북도']
        mcols = [c for c in dfp.columns if c not in ['구분(1)', '구분(2)']]
        dfp[mcols] = dfp[mcols].apply(pd.to_numeric, errors='coerce')
        avg = dfp.groupby('구분(2)')[mcols].mean().mean(axis=1).rename(pol)
        polls.append(avg)
    poll_df = pd.concat(polls, axis=1).reset_index().rename(columns={'구분(2)': '시군'})
    poll_df['시군'] = poll_df['시군'].astype(str).apply(lambda x: x + '시' if not x.endswith(('시', '군')) else x)
    for pol in pollutants:
        poll_df[f'{pol}_n'] = poll_df[pol] / poll_df[pol].max()
    poll_df['poll_comp'] = poll_df[[f'{p}_n' for p in pollutants]].sum(axis=1)
    poll_df['poll_inv'] = 1 / poll_df['poll_comp']
    poll_df['poll_norm'] = poll_df['poll_inv'] / poll_df['poll_inv'].max()

    # --- 6) 통합 및 시각화 ---
    metrics = pd.DataFrame({'시군': regions})
    metrics = metrics.merge(df_park[['시군', 'park_norm']], on='시군')
    metrics = metrics.merge(df_acc2[['시군', 'acc_norm']], on='시군')
    metrics = metrics.merge(fac_df[['시군', 'fac_norm']], on='시군')
    metrics = metrics.merge(crime_tot[['시군', 'crime_norm']], on='시군')
    metrics = metrics.merge(poll_df[['시군', 'poll_norm']], on='시군')

    categories = ['산책 환경', '반려동물 시설', '교통 안전', '치안', '대기 환경']
    theta = categories + [categories[0]]

    fig = go.Figure()

    for _, row in metrics.iterrows():
        values = [
            row['park_norm'],
            row['fac_norm'],
            row['acc_norm'],
            row['crime_norm'],
            row['poll_norm']
        ] + [row['park_norm']]

        is_selected = row['시군'] == selected_region

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=theta,
            name=row['시군'],
            line=dict(width=3 if is_selected else 1.2, color="#2ca02c" if is_selected else 'lightgray'),
            opacity=1.0 if is_selected else 0.3,
            fill='toself' if is_selected else None
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], side="clockwise", angle=90),
            angularaxis=dict(rotation=90, direction="clockwise")
        ),
        showlegend=True,
        legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.3),
        width=520,
        height=500,
        margin=dict(t=20, b=0, l=0, r=0)
    )

    return fig