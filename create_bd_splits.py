import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(BASE_DIR, "bd_agrohome_hourly_90days.csv")
SPLIT_DIR = os.path.join(BASE_DIR, "splits")


def create_splits(train_days=60, val_days=15, test_days=15):
    if not os.path.exists(SOURCE_FILE):
        raise FileNotFoundError(f"Source dataset not found: {SOURCE_FILE}")

    df = pd.read_csv(SOURCE_FILE)
    if "timestamp" not in df.columns:
        raise ValueError("Dataset must contain a 'timestamp' column")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Use unique day boundaries to preserve time continuity.
    df["date"] = df["timestamp"].dt.date
    unique_days = list(df["date"].drop_duplicates())

    total_days = train_days + val_days + test_days
    if len(unique_days) < total_days:
        raise ValueError(
            f"Not enough days in dataset. Required {total_days}, found {len(unique_days)}"
        )

    train_day_set = set(unique_days[:train_days])
    val_day_set = set(unique_days[train_days:train_days + val_days])
    test_day_set = set(unique_days[train_days + val_days:train_days + val_days + test_days])

    train_df = df[df["date"].isin(train_day_set)].copy()
    val_df = df[df["date"].isin(val_day_set)].copy()
    test_df = df[df["date"].isin(test_day_set)].copy()

    for split_df in (train_df, val_df, test_df):
        split_df.drop(columns=["date"], inplace=True)

    os.makedirs(SPLIT_DIR, exist_ok=True)
    train_path = os.path.join(SPLIT_DIR, "bd_train.csv")
    val_path = os.path.join(SPLIT_DIR, "bd_validation.csv")
    test_path = os.path.join(SPLIT_DIR, "bd_test.csv")

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    split_info = {
        "train_rows": len(train_df),
        "validation_rows": len(val_df),
        "test_rows": len(test_df),
        "train_days": train_days,
        "validation_days": val_days,
        "test_days": test_days,
    }
    return split_info


if __name__ == "__main__":
    info = create_splits()
    print("Bangladesh dataset split complete")
    print(info)
