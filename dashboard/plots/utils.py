# plots/utils.py
import pandas as pd

def unify_and_filter_region(df: pd.DataFrame, col: str, second_col: str = None) -> pd.DataFrame:
    df = df.copy()

    # 시군구 단위 기준 정리
    region_keywords = [
        "포항시", "경주시", "김천시", "안동시", "구미시", "영주시", "영천시", "상주시", "문경시", "경산시",
        "의성군", "청송군", "영양군", "영덕군", "청도군", "고령군", "성주군", "칠곡군", "예천군", "봉화군",
        "울진군", "울릉군"
    ]

    pattern = "(" + "|".join(region_keywords) + ")"

    if second_col and second_col in df.columns:
        df['region_raw'] = df[col].astype(str).str.strip() + " " + df[second_col].astype(str).str.strip()
        df['region'] = df['region_raw'].str.extract(pattern)[0]
    else:
        df['region'] = df[col].astype(str).str.strip().str.extract(pattern)[0]

    # 군위군 제거
    return df[df['region'] != '군위군']

