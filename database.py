"""Quản lý tài khoản và lưu phản hồi sinh viên bằng MySQL."""
import hashlib
import sys

import mysql.connector


class Database:

    def __init__(self, host="localhost", user="root", password="mat_khau_mysql_cua_ban",
                 database="lang_nghe_sv"):
        # use_pure: bản C extension làm sập kernel Jupyter khi kết nối lỗi
        self.config = {"host": host, "user": user, "password": password,
                       "database": database, "use_pure": True}
        self._tao_bang()

    def _ket_noi(self):
        return mysql.connector.connect(**self.config)

    def _run(self, sql, params=(), fetch=False, dictionary=False):
        conn = self._ket_noi()
        try:
            cur = conn.cursor(dictionary=dictionary)
            cur.execute(sql, params)
            result = cur.fetchall() if fetch else None
            conn.commit()
            cur.close()
            return result
        finally:
            conn.close()

    def _tao_bang(self):
        self._run("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        self._run("""
            CREATE TABLE IF NOT EXISTS phan_hoi (
                id INT AUTO_INCREMENT PRIMARY KEY,
                feedback VARCHAR(500) NOT NULL,
                sentiment INT,
                so_sao INT
            )
        """)

    def _bam_mat_khau(self, mat_khau):
        return hashlib.sha256(mat_khau.encode()).hexdigest()

    def dang_ky(self, username, mat_khau):
        try:
            self._run("INSERT INTO users (username, password) VALUES (%s, %s)",
                      (username, self._bam_mat_khau(mat_khau)))
            return True
        except mysql.connector.IntegrityError:
            return False  # username đã tồn tại

    def dang_nhap(self, username, mat_khau):
        rows = self._run("SELECT password FROM users WHERE username = %s",
                         (username,), fetch=True)
        return bool(rows) and rows[0][0] == self._bam_mat_khau(mat_khau)

    def luu_phan_hoi(self, feedback, so_sao):
        """Lưu phản hồi. 1-2 sao -> tiêu cực, 3 sao -> trung lập, 4-5 sao -> tích cực."""
        sentiment = 0 if so_sao <= 2 else (2 if so_sao == 3 else 1)
        self._run("INSERT INTO phan_hoi (feedback, sentiment, so_sao) VALUES (%s, %s, %s)",
                  (feedback, sentiment, so_sao))

    def lay_phan_hoi(self):
        return self._run("SELECT feedback, sentiment, so_sao FROM phan_hoi",
                         fetch=True, dictionary=True)


if __name__ == "__main__":
    # console Windows không in được chữ có dấu nếu để mặc định
    sys.stdout.reconfigure(encoding="utf-8")

    try:
        db = Database()
    except Exception as loi:
        print("Không kết nối được MySQL:", loi)
        print("Kiểm tra lại: MySQL đã chạy chưa, đã tạo database lang_nghe_sv chưa,")
        print("và mật khẩu trong Database.__init__ có đúng không.")
        sys.exit(1)

    db.dang_ky("sv01", "123456")
    print("Đăng nhập đúng:", db.dang_nhap("sv01", "123456"))   # True
    print("Đăng nhập sai :", db.dang_nhap("sv01", "sai"))       # False

    db.luu_phan_hoi("thầy giảng rất hay và nhiệt tình", so_sao=5)
    db.luu_phan_hoi("phòng học nóng và thiếu máy chiếu", so_sao=1)
    for ph in db.lay_phan_hoi():
        print(ph)
