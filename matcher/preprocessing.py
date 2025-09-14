import pandas as pd
from langdetect import detect


def load_and_clean_dataset(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df = df.drop(columns=df.columns[df.isna().all()])
    df = df.dropna(how="all").reset_index(drop=True)

    text_cols = ["Skills", "Software", "Creative Styles"]
    for col in text_cols:
        df[col] = df[col].fillna("")

    def tokenize_column(series: pd.Series) -> pd.Series:
        return series.apply(lambda x: [s.strip().lower() for s in str(x).split(",") if s.strip()])

    cols_to_tokenize = {
        "Skills": "Skills_list",
        "Software": "Software_list",
        "Job Types": "JobTypes_list",
        "Platforms": "Platforms_list"
    }
    for col, new_col in cols_to_tokenize.items():
        df[new_col] = tokenize_column(df[col])

    df["Profile_clean"] = df["Profile Description"].astype(str).str.lower().str.strip()
    df["language"] = df["Profile_clean"].apply(lambda x: detect(x) if x.strip() else "unknown")

    def normalize_column(df, col_name, new_col_name=None):
        min_val, max_val = df[col_name].min(), df[col_name].max()
        new_col_name = new_col_name or col_name
        if max_val == min_val:
            df[new_col_name] = 0
        else:
            df[new_col_name] = (df[col_name] - min_val) / (max_val - min_val)
        return df

    df = normalize_column(df, "Monthly Rate", "MonthlyRate_norm")
    df = normalize_column(df, "Hourly Rate", "HourlyRate_norm")
    df = normalize_column(df, "# of Views by Creators", "Views_norm")

    return df
