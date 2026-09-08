"""Tải dữ liệu UIT-VSFC về data/feedback.csv, giữ nguyên cột split."""
import os
import sys

import pandas as pd
from datasets import load_dataset

COT = ["feedback", "sentiment", "topic", "split"]
# Đổi mã nhãn cảm xúc: gốc 0=tiêu cực, 1=trung lập, 2=tích cực
#                  -> đồ án 0=tiêu cực, 1=tích cực,  2=trung lập (cho dễ đọc biểu đồ)
DOI_CX = {0: 0, 2: 1, 1: 2}
TEN_TAP = {"train": "train", "validation": "dev", "test": "test"}


def tai(path="data/feedback.csv"):
    """Tải 3 tập của bộ dữ liệu rồi gộp thành một file CSV có cột split."""
    ds = load_dataset("uitnlp/vietnamese_students_feedback")

    cac_tap = []
    for tap in ds:
        phan = ds[tap].to_pandas()
        phan["split"] = TEN_TAP[tap]
        cac_tap.append(phan)

    df = pd.concat(cac_tap, ignore_index=True)
    df["feedback"] = df["sentence"].str.strip()
    df["sentiment"] = df["sentiment"].map(DOI_CX)
    df = df[df["feedback"] != ""]

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df[COT].to_csv(path, index=False, encoding="utf-8")

    print("Da tao", path, "voi", len(df), "dong")
    print(df["split"].value_counts().to_string())


if __name__ == "__main__":
    # Console Windows mặc định không in được chữ có dấu
    sys.stdout.reconfigure(encoding="utf-8")

    tai()
