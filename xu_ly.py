"""Gom thao tác xử lý dữ liệu và mô hình phân loại vào class.

Cả notebook và app.py đều import từ file này để dùng lại cùng một bản code.
"""
import re
import sys
import threading
import time

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

TEN_CX = {0: "Tiêu cực", 1: "Tích cực", 2: "Trung lập"}
TEN_CD = {0: "Giảng viên", 1: "Chương trình", 2: "Cơ sở vật chất", 3: "Khác"}


class XuLyDuLieu:
    """Đọc, làm sạch và thống kê dữ liệu phản hồi."""

    def __init__(self, path="data/feedback.csv"):
        self.path = path
        self.df = None   # dữ liệu sẽ được nạp vào đây

    def lam_sach(self, text):
        """Chữ thường, bỏ ký tự đặc biệt, gộp khoảng trắng."""
        text = str(text).lower()
        text = re.sub(r"[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễ"
                      r"ìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def nap(self):
        """Đọc CSV, làm sạch văn bản, bỏ dòng trùng và dòng rỗng."""
        df = pd.read_csv(self.path)
        df = df.drop_duplicates().dropna(subset=["feedback"])
        df["feedback_sach"] = df["feedback"].apply(self.lam_sach)
        df = df[df["feedback_sach"].str.len() > 0]
        self.df = df.reset_index(drop=True)
        return self.df

    def thong_ke_cam_xuc(self):
        """Đếm số phản hồi theo từng loại cảm xúc."""
        dem = self.df["sentiment"].value_counts().to_dict()
        return {TEN_CX[k]: v for k, v in dem.items()}


# Hai bài toán (cảm xúc, chủ đề) dùng chung cách huấn luyện và dự đoán, chỉ khác
# cột nhãn. Nên phần chung viết một lần ở lớp cha, lớp con chỉ khai báo phần riêng.

class MoHinhPhanLoai:
    """Lớp cha chứa phần dùng chung của một bài toán phân loại văn bản."""

    ten_nhan = {}    # lớp con khai báo: mã nhãn -> tên nhãn
    cot_nhan = ""    # lớp con khai báo: tên cột nhãn trong DataFrame

    def __init__(self, ngram=(1, 2), min_df=2, class_weight="balanced"):
        self.vec = TfidfVectorizer(ngram_range=ngram, min_df=min_df)
        self.mo_hinh = LogisticRegression(max_iter=1000, class_weight=class_weight)
        self.da_train = False

    def mo_ta(self):
        """Mô tả ngắn bài toán mà lớp này giải."""
        return (f"phân loại {len(self.ten_nhan)} lớp ("
                + ", ".join(self.ten_nhan.values()) + ")")

    def huan_luyen(self, df):
        """Chỉ học trên tập train để không nhìn trước tập test."""
        if "split" in df.columns:
            df = df[df["split"] == "train"]
        X = self.vec.fit_transform(df["feedback_sach"])
        self.mo_hinh.fit(X, df[self.cot_nhan])
        self.da_train = True
        return self          # trả về self để viết được: MoHinhCamXuc().huan_luyen(df)

    def du_doan(self, cau, xu_ly):
        """Dự đoán cho một câu mới. Truyền đối tượng XuLyDuLieu để dùng chung lam_sach."""
        if not self.da_train:
            return "Chưa huấn luyện", {}
        vector = self.vec.transform([xu_ly.lam_sach(cau)])
        nhan = self.mo_hinh.predict(vector)[0]
        xac_suat = self.mo_hinh.predict_proba(vector)[0]
        chi_tiet = {self.ten_nhan[c]: float(round(p * 100, 1))
                    for c, p in zip(self.mo_hinh.classes_, xac_suat)}
        return self.ten_nhan[nhan], chi_tiet


class MoHinhCamXuc(MoHinhPhanLoai):
    """Phân loại cảm xúc. Kế thừa hết từ lớp cha, chỉ khai báo nhãn."""

    ten_nhan = TEN_CX
    cot_nhan = "sentiment"


class MoHinhChuDe(MoHinhPhanLoai):
    """Phân loại chủ đề. Kế thừa lớp cha nhưng ghi đè 2 chỗ."""

    ten_nhan = TEN_CD
    cot_nhan = "topic"

    def __init__(self):
        # chủ đề không ép cân bằng lớp: giữ đúng tỉ lệ thật (đa số phản hồi về giảng viên)
        super().__init__(class_weight=None)

    def mo_ta(self):
        # ghi đè: lấy kết quả lớp cha rồi thêm phần riêng
        return "chủ đề: " + super().mo_ta()


# ===== Xử lý nhiều luồng =====
def chia_phan(danh_sach, so_phan):
    """Cắt một danh sách thành `so_phan` phần gần bằng nhau."""
    kich_thuoc = (len(danh_sach) + so_phan - 1) // so_phan
    return [danh_sach[i:i + kich_thuoc]
            for i in range(0, len(danh_sach), kich_thuoc)]


def chay_song_song(viec, cac_phan):
    """Mỗi phần việc chạy trên một luồng, chờ tất cả xong mới trả về."""
    cac_luong = [threading.Thread(target=viec, args=(i, phan))
                 for i, phan in enumerate(cac_phan)]
    for luong in cac_luong:
        luong.start()
    for luong in cac_luong:
        luong.join()          # chờ luồng chạy xong


def lam_sach_da_luong(cac_cau, ham_lam_sach, so_luong=4):
    """Làm sạch danh sách câu bằng `so_luong` luồng chạy song song."""
    cac_phan = chia_phan(cac_cau, so_luong)
    ket_qua = [None] * len(cac_phan)

    def lam_mot_phan(vi_tri, phan):
        ket_qua[vi_tri] = [ham_lam_sach(cau) for cau in phan]

    chay_song_song(lam_mot_phan, cac_phan)
    return [cau for phan in ket_qua for cau in phan]


def doc_nhieu_file(cac_path, so_luong=4):
    """Đọc nhiều file CSV cùng lúc bằng nhiều luồng. Trả về danh sách DataFrame."""
    cac_phan = chia_phan(list(cac_path), so_luong)
    ket_qua = [None] * len(cac_phan)

    def doc_mot_phan(vi_tri, phan):
        ket_qua[vi_tri] = [pd.read_csv(path) for path in phan]

    chay_song_song(doc_mot_phan, cac_phan)
    return [df for phan in ket_qua for df in phan]


def dem_tu_da_luong(cac_cau, so_luong=4):
    """Đếm số lần xuất hiện của từng từ bằng nhiều luồng.

    Nhiều luồng cùng cộng vào `dem_chung` nên phải dùng Lock: không khóa thì hai
    luồng có thể ghi đè lẫn nhau làm sai số đếm (race condition).
    """
    dem_chung = {}
    khoa = threading.Lock()

    def dem_mot_phan(vi_tri, phan):
        rieng = {}                      # đếm riêng trước cho khỏi tranh chấp
        for cau in phan:
            for tu in str(cau).split():
                rieng[tu] = rieng.get(tu, 0) + 1

        khoa.acquire()                  # xin khóa, luồng khác phải chờ
        try:
            for tu, so_lan in rieng.items():
                dem_chung[tu] = dem_chung.get(tu, 0) + so_lan
        finally:
            khoa.release()              # nhả khóa

    chay_song_song(dem_mot_phan, chia_phan(cac_cau, so_luong))
    return dem_chung


def do_thoi_gian(ham, *args, **kwargs):
    """Chạy một hàm và trả về (kết quả, số giây đã chạy)."""
    bat_dau = time.perf_counter()
    ket_qua = ham(*args, **kwargs)
    return ket_qua, time.perf_counter() - bat_dau


if __name__ == "__main__":
    # Console Windows mặc định không in được chữ có dấu
    sys.stdout.reconfigure(encoding="utf-8")

    xu_ly = XuLyDuLieu("data/feedback.csv")
    df = xu_ly.nap()
    print("Số phản hồi:", len(df))
    print("Thống kê cảm xúc:", xu_ly.thong_ke_cam_xuc())

    # Hai lớp con dùng chung code của lớp cha: một vòng lặp chạy cho cả 2 bài toán
    for lop in (MoHinhCamXuc, MoHinhChuDe):
        mo_hinh = lop().huan_luyen(df)
        nhan, chi_tiet = mo_hinh.du_doan("thầy giảng rất hay và dễ hiểu", xu_ly)
        print(f"[{mo_hinh.mo_ta()}] -> {nhan} {chi_tiet}")

    # So sánh tốc độ làm sạch bằng 1 luồng và 4 luồng
    cau = df["feedback"].tolist()
    _, giay_1 = do_thoi_gian(lambda: [xu_ly.lam_sach(c) for c in cau])
    _, giay_4 = do_thoi_gian(lam_sach_da_luong, cau, xu_ly.lam_sach, 4)
    print(f"Làm sạch {len(cau)} câu: 1 luồng {giay_1:.3f}s | 4 luồng {giay_4:.3f}s")
