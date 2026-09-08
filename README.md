# Hệ thống Lắng nghe Sinh viên

Đồ án cuối kỳ môn **Ngôn ngữ lập trình Python** (mã HP 124100).

Phân tích và trực quan hóa phản hồi của sinh viên về môn học, giúp nhà trường
nắm được mức độ hài lòng theo 3 khía cạnh: giảng viên, chương trình học, cơ sở
vật chất, và phát hiện điều cần cải thiện.

**Trọng tâm: phân tích dữ liệu + trực quan hóa.** Máy học chỉ là tính năng phụ
minh họa khả năng ứng dụng (theo đúng yêu cầu của thầy: "không phải dữ liệu nào
cũng ráng nhét ML vào").

## Bài nộp gồm những gì

| Tệp | Nội dung |
|---|---|
| `BaoCao_DoAn.docx` | **Báo cáo chính**, 7 chương, 23 bảng, 8 hình. Nộp **riêng**, để ở thư mục cha ngay bên ngoài thư mục này. Còn 3 chỗ `[ĐIỀN...]` ở trang bìa |
| `HeThong_LangNghe_SinhVien.ipynb` | Notebook đã chạy sẵn, **có đủ kết quả và biểu đồ** |
| `app.py` | Web dashboard Streamlit (dùng để demo) |
| `xu_ly.py`, `database.py`, `tai_du_lieu.py` | Các module Python |

## Kết quả phân tích chính (số liệu thật từ 16.175 phản hồi)

| Chủ đề | Số phản hồi | % tiêu cực | % tích cực |
|---|---|---|---|
| Cơ sở vật chất | 712 (4,4%) | **95,6%** | 2,5% |
| Chương trình học | 3.040 (18,8%) | **76,6%** | 18,1% |
| Khác | 816 (5,0%) | 39,8% | 31,9% |
| Giảng viên | 11.607 (71,8%) | 35,4% | **62,1%** |

Ba phát hiện chính:

1. **Cơ sở vật chất là điểm yếu nặng nhất**, 95,6% tiêu cực, chỉ 2,5% khen. Nhưng
   chỉ 4,4% sinh viên nhắc tới: *ít người nói, nhưng ai nói cũng chê.* Cụm từ hay
   gặp: thiết bị (169), phòng học (142), máy chiếu (118), phòng máy (79).
2. **Chương trình học bị chê 76,6%**, tập trung vào việc thiếu giờ **thực hành**
   (1.035 lần) và quá nhiều bài tập, lý thuyết.
3. **Giảng viên là điểm mạnh**, 62,1% tích cực, được khen "nhiệt tình" (2.495 lần),
   "dễ hiểu" (1.358), "tận tâm" (771).

Phát hiện phụ: phản hồi tiêu cực dài trung bình 15,3 từ so với 10,4 từ của phản hồi
tích cực, **người không hài lòng viết dài hơn 47%**.

## Cấu trúc thư mục

```
BaoCao_DoAn.docx                      # BÁO CÁO CHÍNH (7 chương), nộp riêng, ngoài thư mục source
HeThong_LangNghe_SinhVien/            # phần source code
├── HeThong_LangNghe_SinhVien.ipynb   # Notebook chính, đã chạy sẵn có kết quả
├── app.py                            # Web dashboard Streamlit
├── tai_du_lieu.py                    # Công cụ tải dữ liệu thật UIT-VSFC
├── xu_ly.py                          # Lớp OOP + kế thừa, hàm đa luồng (Ch3, Ch6)
├── database.py                       # Lớp MySQL: đăng nhập + lưu phản hồi (Ch5)
├── requirements.txt                  # Thư viện cần cài
├── data/
│   ├── feedback.csv                  # Dữ liệu gốc 16.175 câu (có cột split chia tập)
│   ├── feedback_clean.csv            # Dữ liệu đã tiền xử lý (mục 2.9 tự sinh)
│   ├── thong_ke.json                 # Bảng thống kê dạng JSON (mục 2.9 tự sinh)
│   ├── thong_ke.xml                  # Cùng bảng đó dạng XML (mục 2.9 tự sinh)
│   └── theo_chu_de/                  # 4 file CSV tách theo chủ đề (mục 2.9 tự sinh)
└── README.md                         # File này
```

## Cài đặt

```bash
pip install -r requirements.txt
```

> **Lưu ý quan trọng khi chạy:** máy phải dùng **đúng bản Python đã cài thư viện**.
> Nếu máy có nhiều bản Python (ví dụ 3.10 và 3.12) mà chỉ cài thư viện cho một bản,
> chạy bằng bản kia sẽ báo `ModuleNotFoundError: No module named 'pandas'`.
> Kiểm tra bằng `python -c "import pandas, streamlit; print('OK')"` trước khi chạy.

## Cách chạy

**1. Tải dữ liệu (chỉ cần khi thư mục `data/` chưa có `feedback.csv`):**
```bash
python tai_du_lieu.py
```
Mục 0 trong notebook cũng làm việc này và **tự bỏ qua nếu file đã có**, nên bình
thường không cần chạy lệnh này.

**2. Notebook (phân tích + bảo vệ):**
```bash
jupyter notebook HeThong_LangNghe_SinhVien.ipynb
```
File đã có sẵn kết quả và biểu đồ nên mở ra là xem được ngay. Muốn chạy lại thì
Shift+Enter từ trên xuống. Có thể mở bằng VS Code / Colab.

**3. Web dashboard (demo):**
```bash
streamlit run app.py
```
Phải dùng `streamlit run`, **không** dùng `python app.py`, chạy bằng `python` thì
Streamlit không mở được giao diện.

Nếu máy chưa có MySQL, dashboard vẫn vào được bằng nút **"Vào xem dashboard (chế độ
khách)"**, chỉ phần đăng nhập tạm tắt, toàn bộ phần phân tích vẫn xem được.

## Nội dung notebook

| Mục | Nội dung |
|---|---|
| 0 | Tải dữ liệu thật UIT-VSFC (tự bỏ qua nếu đã có file) |
| 1 | Nạp dữ liệu và tìm hiểu dữ liệu (số mẫu, thuộc tính, ý nghĩa từng cột) |
| 2 | Tiền xử lý: kiểu dữ liệu → giá trị thiếu → dữ liệu không hợp lệ → trùng lặp → chuẩn hóa văn bản → gán nhãn → nhiễu & ngoại lai → lưu file sạch (CSV + JSON + XML) |
| 3 | Phân tích: phân bố cảm xúc, chủ đề, bảng chéo, độ dài, từ khóa và cụm 2 từ |
| 4 | Trực quan hóa: biểu đồ cột, tròn, cột nhóm |
| 5 | **Nhận xét và kết luận**, phát hiện chính + kiến nghị cho nhà trường |
| 6 | Chia train/dev/test → đặc trưng TF-IDF → xử lý mất cân bằng → đánh giá trên test (cảm xúc ở 6.4, chủ đề ở 6.5) |
| 7 | Ứng dụng mô hình: dự đoán cảm xúc cho phản hồi mới |
| 8 | Kỹ thuật lập trình: 8.1 đóng gói · 8.2 **kế thừa + ghi đè** (Ch3) · 8.3 **đa luồng** (Ch6) |
| 9 | Cơ sở dữ liệu MySQL (Chương 5) |
| 10 | Kết luận |

### Quy trình xử lý dữ liệu 14 bước, làm ở đâu

| Bước | Nội dung | Mục |
|---|---|---|
| 1 | Thu thập và hiểu dữ liệu | 0, 1 |
| 2 | Kiểm tra & chuyển đổi kiểu dữ liệu | 2.1 |
| 3 | Xử lý giá trị thiếu | 2.2, 2.3 |
| 4 | Xử lý dữ liệu không hợp lệ | 2.4 |
| 5 | Xử lý dữ liệu trùng lặp | 2.2, 2.3 |
| 6 | Xử lý nhiễu và ngoại lai (boxplot, IQR, z-score) | 2.7, 2.8 |
| 7 | Chuẩn hóa dữ liệu | 2.5 |
| 8 | Mã hóa dữ liệu phân loại | 2.6 |
| 9 | Xử lý dữ liệu mất cân bằng (class weighting, under/oversampling) | 6.3 |
| 10 | Xử lý đặc trưng (TF-IDF, n-gram, lọc đặc trưng) | 6.2 |
| 11 | Gán nhãn dữ liệu | 2.6 |
| 12 | Chia train / dev / test | 6.1 |
| 13 | Lưu dữ liệu đã xử lý (CSV + JSON + XML) | 2.9 |
| 14 | Phân tích, trực quan hóa, huấn luyện mô hình | 3, 4, 6.4, 6.5, 7 |

## Web dashboard có gì

- Chỉ số tổng quan (tổng phản hồi, tỷ lệ tích cực/tiêu cực/trung lập)
- **Ô dự đoán cảm xúc trực tiếp**: gõ một câu phản hồi → hệ thống phân loại ngay
  kèm xác suất từng lớp
- Biểu đồ phân bố cảm xúc, phân tích theo chủ đề, bảng chéo
- Từ khóa phổ biến, bộ lọc theo chủ đề
- **Upload CSV khảo sát của trường khác** → tự gán nhãn → tải kết quả về
- Đăng nhập / đăng ký bằng MySQL, có chế độ khách khi chưa có MySQL

## Dữ liệu

**UIT-VSFC** (Vietnamese Students' Feedback Corpus): **16.175 câu** phản hồi sinh viên
thật, thu thập 2013–2016 qua hệ thống khảo sát cuối học kỳ (chấm điểm 1–5 + góp ý
bằng chữ, cùng dạng với form khảo sát của trường).

Mỗi câu có 2 nhãn: **cảm xúc** (tiêu cực / tích cực / trung lập) và **chủ đề**
(giảng viên / chương trình / cơ sở vật chất / khác). File `data/feedback.csv` còn có
cột `split` cho biết mỗi câu thuộc tập train, dev hay test.

Phân bố cảm xúc: tích cực 8.038 câu (49,7%), tiêu cực 7.439 câu (46,0%),
trung lập 698 câu (**4,3%**, dữ liệu lệch nhãn tự nhiên).

Nguồn: Kiet Van Nguyen và cộng sự, "UIT-VSFC: Vietnamese Students' Feedback
Corpus for Sentiment Analysis", KSE 2018.

## Chương áp dụng

| Chương | Áp dụng | Mức độ |
|--------|---------|--------|
| Ch2: Python cơ bản | `try/except` ở mục 0 và mục 9 | Cơ bản |
| Ch3: OOP | `XuLyDuLieu` (đóng gói); `MoHinhPhanLoai` → `MoHinhCamXuc`, `MoHinhChuDe` (**kế thừa + ghi đè**, `xu_ly.py`, mục 8.1–8.2) | Đầy đủ |
| Ch4: XML/JSON | Ghi **và đọc lại** `thong_ke.json` + `thong_ke.xml` (mục 2.9) | Đầy đủ |
| Ch5: CSDL MySQL | Đăng nhập + lưu phản hồi (`database.py`, mục 9) | Đầy đủ |
| Ch6: Đa luồng | So sánh việc nặng CPU và việc chờ đọc file (mục 8.3) | Đầy đủ |
| Ch8: Pandas, Matplotlib | Phân tích + vẽ biểu đồ (mục 2, 3, 4) | **Trọng tâm** |
| Ch9: Máy học | Phân loại cảm xúc + chủ đề (mục 6, 7) | Phụ |

Ngoài chương trình (tự tìm hiểu thêm, nêu trung thực khi bảo vệ): Streamlit,
scikit-learn (TF-IDF, Logistic Regression), thư viện datasets.
