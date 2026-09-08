"""Web dashboard phân tích phản hồi sinh viên. Chạy: streamlit run app.py"""
import re
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from database import Database

st.set_page_config(page_title="Hệ thống Lắng nghe Sinh viên",
                   page_icon="🎓", layout="wide")

TEN_CX = {0: "Tiêu cực", 1: "Tích cực", 2: "Trung lập"}
TEN_CD = {0: "Giảng viên", 1: "Chương trình", 2: "Cơ sở vật chất", 3: "Khác"}
MAU_CX = {"Tiêu cực": "#c0392b", "Tích cực": "#2e8b57", "Trung lập": "#7f8c8d"}

STOPWORDS = {
    "của", "và", "là", "có", "cho", "được", "các", "những", "một", "để", "với",
    "khi", "này", "đã", "rất", "em", "thầy", "cô", "còn", "nên", "cần", "quá",
    "trong", "về", "ở", "ra", "lại", "như", "mà", "thì",
    "sinh", "viên", "giảng", "học", "dạy", "bài", "thực", "môn", "lớp",
    "tiết", "buổi", "hay", "hơn", "theo", "cũng", "vẫn", "đều",
    "không", "nhiều", "ít", "tôi", "mình", "nhưng", "vào", "làm", "giáo",
}


# từ khóa đoán chủ đề cho file chưa có nhãn
KEYWORDS_CD = {
    0: ["thầy", "cô", "giảng viên", "giáo viên", "dạy", "giảng", "bài giảng"],
    1: ["chương trình", "môn học", "tín chỉ", "giáo trình", "nội dung", "học phần", "đề cương"],
    2: ["phòng", "máy lạnh", "máy tính", "wifi", "cơ sở", "thiết bị", "bàn ghế", "điều hòa"],
}


def phan_loai_chu_de(text):
    chu_de_tot_nhat = 3          # 3 = Khác
    diem_cao_nhat = 0
    for chu_de, tu_khoa in KEYWORDS_CD.items():
        diem = 0
        for tu in tu_khoa:
            if tu in text:
                diem += 1
        if diem > diem_cao_nhat:
            diem_cao_nhat = diem
            chu_de_tot_nhat = chu_de
    return chu_de_tot_nhat


def lam_sach(text):
    text = str(text).lower()
    text = re.sub(r"[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễ"
                  r"ìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def ve(fig):
    st.pyplot(fig)
    plt.close(fig)


@st.cache_data
def nap_du_lieu(path="data/feedback.csv"):
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except FileNotFoundError:
        st.error(f"Không tìm thấy file dữ liệu: {path}")
        st.stop()
    df = df.drop_duplicates().dropna(subset=["feedback"])
    df = df[df["feedback"].astype(str).str.strip() != ""]
    df["feedback_sach"] = df["feedback"].apply(lam_sach)
    df["ten_cam_xuc"] = df["sentiment"].map(TEN_CX)
    df["ten_chu_de"] = df["topic"].map(TEN_CD)
    return df


@st.cache_resource
def huan_luyen_mo_hinh():
    df = nap_du_lieu()
    # chỉ học trên tập train, không nhìn trước tập test
    df_train = df[df["split"] == "train"] if "split" in df.columns else df

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
    X = vec.fit_transform(df_train["feedback_sach"])

    mo_hinh = LogisticRegression(max_iter=1000, class_weight="balanced")
    mo_hinh.fit(X, df_train["sentiment"])
    return vec, mo_hinh


def top_tu(df_con, n=8):
    tu = " ".join(df_con["feedback_sach"]).split()
    tu = [t for t in tu if t not in STOPWORDS and len(t) > 1]
    return Counter(tu).most_common(n)


# --- Đăng nhập / Đăng ký ---
@st.cache_resource
def ket_noi_db():
    try:
        return Database()
    except Exception:
        return None


db = ket_noi_db()
if "da_dang_nhap" not in st.session_state:
    st.session_state["da_dang_nhap"] = False
if "ten_nguoi_dung" not in st.session_state:
    st.session_state["ten_nguoi_dung"] = ""

if not st.session_state["da_dang_nhap"]:
    st.title("🎓 Hệ thống Lắng nghe Sinh viên")

    # không có MySQL thì vẫn cho xem dashboard, phần phân tích không phụ thuộc database
    if db is None:
        st.warning("Chưa kết nối được MySQL nên phần đăng nhập tạm thời không dùng "
                   "được. Bạn vẫn xem được toàn bộ phần phân tích ở chế độ khách.")
        if st.button("Vào xem dashboard (chế độ khách)"):
            st.session_state["da_dang_nhap"] = True
            st.session_state["ten_nguoi_dung"] = "Khách"
            st.rerun()
        st.caption("Muốn bật đăng nhập thật: chạy MySQL, tạo database "
                   "`lang_nghe_sv`, rồi sửa mật khẩu trong `database.py`.")
        st.stop()

    st.subheader("Vui lòng đăng nhập để tiếp tục")

    lua_chon = st.radio("Chọn thao tác", ["Đăng nhập", "Đăng ký"],
                        horizontal=True, label_visibility="collapsed")
    with st.form("form_tai_khoan"):
        username = st.text_input("Tên đăng nhập")
        mat_khau = st.text_input("Mật khẩu", type="password")
        gui = st.form_submit_button(lua_chon)

    if gui:
        if not username or not mat_khau:
            st.warning("Vui lòng nhập đủ thông tin.")
        elif db is None:
            st.error("Không kết nối được MySQL. Kiểm tra lại cài đặt database.")
        elif lua_chon == "Đăng nhập":
            if db.dang_nhap(username, mat_khau):
                st.session_state["da_dang_nhap"] = True
                st.session_state["ten_nguoi_dung"] = username
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu.")
        elif db.dang_ky(username, mat_khau):
            st.success("Đăng ký thành công! Vui lòng đăng nhập.")
        else:
            st.error("Tên đăng nhập đã tồn tại.")
    st.stop()

# --- Trang chính ---
df = nap_du_lieu()
vec, mo_hinh = huan_luyen_mo_hinh()

st.title("🎓 Hệ thống Lắng nghe Sinh viên")
st.caption("Phân tích và trực quan hóa phản hồi của sinh viên về môn học, "
           "giúp nhà trường nắm bắt mức độ hài lòng và điểm cần cải thiện.")

st.sidebar.write(f"👤 **{st.session_state['ten_nguoi_dung']}**")
if st.sidebar.button("Đăng xuất"):
    st.session_state["da_dang_nhap"] = False
    st.session_state["ten_nguoi_dung"] = ""
    st.rerun()
st.sidebar.divider()

# --- Upload file từ trường khác ---
st.sidebar.header("Nguồn dữ liệu")
file_tai_len = st.sidebar.file_uploader(
    "Upload CSV từ trường khác", type="csv",
    help="Chỉ cần một cột chứa nội dung phản hồi. Hệ thống tự gán cảm xúc và chủ đề.")

if file_tai_len:
    try:
        df_tho = pd.read_csv(file_tai_len, encoding="utf-8")
    except UnicodeDecodeError:
        file_tai_len.seek(0)
        df_tho = pd.read_csv(file_tai_len, encoding="utf-8-sig")

    cot_chon = st.selectbox("Chọn cột chứa nội dung phản hồi:", df_tho.columns.tolist())
    df = df_tho[[cot_chon]].rename(columns={cot_chon: "feedback"})
    df = df.dropna().drop_duplicates()
    df = df[df["feedback"].astype(str).str.strip() != ""]
    df["feedback_sach"] = df["feedback"].apply(lam_sach)
    df["sentiment"] = mo_hinh.predict(vec.transform(df["feedback_sach"]))
    df["topic"] = df["feedback_sach"].apply(phan_loai_chu_de)
    df["ten_cam_xuc"] = df["sentiment"].map(TEN_CX)
    df["ten_chu_de"] = df["topic"].map(TEN_CD)

    st.success(f"Đã phân tích {len(df):,} phản hồi từ file upload "
               "(cảm xúc do mô hình dự đoán, chủ đề đoán bằng từ khóa).")
    st.download_button(
        "Tải kết quả đã gán nhãn (.csv)",
        df[["feedback", "ten_cam_xuc", "ten_chu_de"]].to_csv(index=False).encode("utf-8-sig"),
        file_name="ket_qua_phan_tich.csv", mime="text/csv")

st.sidebar.header("Bộ lọc")
chu_de_chon = st.sidebar.multiselect("Lọc theo chủ đề:",
                                     options=list(TEN_CD.values()),
                                     default=list(TEN_CD.values()))
df_loc = df[df["ten_chu_de"].isin(chu_de_chon)]

tong = len(df_loc)
tieu_cuc = int((df_loc["sentiment"] == 0).sum())
tich_cuc = int((df_loc["sentiment"] == 1).sum())
trung_lap = int((df_loc["sentiment"] == 2).sum())


def phan_tram(so):
    if tong == 0:
        return "0"
    return f"{so} ({so / tong * 100:.0f}%)"


c1, c2, c3, c4 = st.columns(4)
c1.metric("Tổng phản hồi", tong)
c2.metric("Tích cực", phan_tram(tich_cuc))
c3.metric("Tiêu cực", phan_tram(tieu_cuc))
c4.metric("Trung lập", phan_tram(trung_lap))
st.divider()

st.subheader("🔮 Thử dự đoán cảm xúc một phản hồi mới")
cau_nhap = st.text_area("Nhập phản hồi của sinh viên:",
                        placeholder="Ví dụ: Thầy giảng rất hay và dễ hiểu", height=80)

if st.button("Phân tích cảm xúc"):
    if not cau_nhap.strip():
        st.warning("Vui lòng nhập một câu phản hồi.")
    else:
        vector = vec.transform([lam_sach(cau_nhap)])
        ten = TEN_CX[mo_hinh.predict(vector)[0]]
        if ten == "Tích cực":
            st.success(f"Cảm xúc dự đoán: **{ten}**")
        elif ten == "Tiêu cực":
            st.error(f"Cảm xúc dự đoán: **{ten}**")
        else:
            st.info(f"Cảm xúc dự đoán: **{ten}**")
        st.table(pd.DataFrame({
            "Cảm xúc": [TEN_CX[i] for i in mo_hinh.classes_],
            "Xác suất (%)": [f"{p * 100:.1f}" for p in mo_hinh.predict_proba(vector)[0]],
        }))
st.divider()

# --- Biểu đồ ---
if tong == 0:
    st.warning("Không có dữ liệu để hiển thị. Thử bỏ bộ lọc.")
    st.stop()

pb_cx = df_loc["ten_cam_xuc"].value_counts()
mau = [MAU_CX.get(x, "#888") for x in pb_cx.index]
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Phân bố cảm xúc")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.bar(pb_cx.index, pb_cx.values, color=mau)
    ax.set_ylabel("Số lượng")
    ve(fig)

with col_b:
    st.subheader("Tỷ lệ cảm xúc")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.pie(pb_cx.values, labels=pb_cx.index, autopct="%1.1f%%",
           colors=mau, startangle=90)
    ve(fig)

st.subheader("Cảm xúc theo từng chủ đề")
st.caption("Cho biết chủ đề nào bị chê nhiều, chủ đề nào được khen nhiều.")
bang_cheo = pd.crosstab(df_loc["ten_chu_de"], df_loc["ten_cam_xuc"])
fig, ax = plt.subplots(figsize=(9, 4))
bang_cheo.plot(kind="bar", ax=ax,
               color=[MAU_CX.get(c, "#888") for c in bang_cheo.columns])
ax.set_ylabel("Số lượng")
ax.set_xlabel("")
ax.legend(title="Cảm xúc")
plt.xticks(rotation=0)
ve(fig)

st.subheader("Bảng tỷ lệ cảm xúc trong từng chủ đề (%)")
st.dataframe((pd.crosstab(df_loc["ten_chu_de"], df_loc["ten_cam_xuc"],
                          normalize="index") * 100).round(1))

st.subheader("Từ khóa xuất hiện nhiều nhất")
col_p, col_n = st.columns(2)

with col_p:
    st.markdown("**Trong phản hồi tích cực**")
    tu_tich_cuc = top_tu(df_loc[df_loc["sentiment"] == 1])
    if tu_tich_cuc:
        st.table(pd.DataFrame(tu_tich_cuc, columns=["Từ", "Số lần"]))

with col_n:
    st.markdown("**Trong phản hồi tiêu cực**")
    tu_tieu_cuc = top_tu(df_loc[df_loc["sentiment"] == 0])
    if tu_tieu_cuc:
        st.table(pd.DataFrame(tu_tieu_cuc, columns=["Từ", "Số lần"]))

with st.expander("Xem bảng dữ liệu phản hồi"):
    st.dataframe(df_loc[["feedback", "ten_cam_xuc", "ten_chu_de"]],
                 use_container_width=True)
