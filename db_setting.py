from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# cursor.execute("""SELECT BienTheSanPham.id, BienTheSanPham.hinh_anh, SanPham.ten_san_pham, SanPham.gia_ban, KichCo.ten_kich_co, 
#        MauSac.ten_mau, DanhMucSanPham.ten_danh_muc
# FROM BienTheSanPham
# JOIN SanPham ON BienTheSanPham.id_san_pham = SanPham.id
# JOIN KichCo ON BienTheSanPham.id_kich_co = KichCo.id
# JOIN MauSac ON BienTheSanPham.id_mau_sac = MauSac.id
# JOIN DanhMucSanPham ON SanPham.id_danh_muc = DanhMucSanPham.id
# WHERE KichCo.ten_kich_co = 'M' AND MauSac.ten_mau = 'Trắng' AND DanhMucSanPham.ten_danh_muc = 'Đồ bơi nữ';""")
# res = cursor.fetchall()
# print(res)
# conn.commit()
# conn.close()

try:
    cursor.execute("""
    DELETE FROM GioHang
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM GioHang
        GROUP BY id_nguoi_dung, id_bien_the
    );
    """)
    print("Duplicates removed successfully.")
    conn.commit()

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
    conn.rollback() # Rollback changes if an error occurs

finally:
    conn.close()

# """UPDATE BienTheSanPham
# SET hinh_anh = "do_tam_tre_em_trang.jpg"
# WHERE id_san_pham = 3 AND id_mau_sac = 4;
# """)




# -----------------------------------------------------------------------SET UP DATABASE------------------------------------------------------------------- #
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# @app.route('/create-tables') 
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS DanhMucSanPham (
        id INTEGER PRIMARY KEY,
        ten_danh_muc TEXT
    );

    CREATE TABLE IF NOT EXISTS SanPham (
        id INTEGER PRIMARY KEY,
        ten_san_pham TEXT,
        mo_ta TEXT,
        gia_ban REAL,
        id_danh_muc INTEGER,
        FOREIGN KEY (id_danh_muc) REFERENCES DanhMucSanPham(id)
    );

    CREATE TABLE IF NOT EXISTS KichCo (
        id INTEGER PRIMARY KEY,
        ten_kich_co TEXT
    );

    CREATE TABLE IF NOT EXISTS MauSac (
        id INTEGER PRIMARY KEY,
        ten_mau TEXT
    );

    CREATE TABLE IF NOT EXISTS BienTheSanPham (
        id INTEGER PRIMARY KEY,
        id_san_pham INTEGER,
        id_kich_co INTEGER,
        id_mau_sac INTEGER,
        so_luong_ton INTEGER,
        hinh_anh TEXT,
        FOREIGN KEY (id_san_pham) REFERENCES SanPham(id),
        FOREIGN KEY (id_kich_co) REFERENCES KichCo(id),
        FOREIGN KEY (id_mau_sac) REFERENCES MauSac(id)
    );

    CREATE TABLE IF NOT EXISTS Banner (
        id INTEGER PRIMARY KEY,
        hinh_anh TEXT,
        vi_tri TEXT
    );

    CREATE TABLE IF NOT EXISTS NguoiDung (
        id INTEGER PRIMARY KEY,
        ten_nguoi_dung TEXT,
        email TEXT,
        ngay_tao_tai_khoan DATE,
        mat_khau TEXT
    );

    CREATE TABLE IF NOT EXISTS GioHang (
        id INTEGER PRIMARY KEY,
        id_nguoi_dung INTEGER,
        id_bien_the INTEGER,
        so_luong INTEGER,
        FOREIGN KEY (id_nguoi_dung) REFERENCES NguoiDung(id),
        FOREIGN KEY (id_bien_the) REFERENCES BienTheSanPham(id)
    );

    CREATE TABLE IF NOT EXISTS DonHang (
        id INTEGER PRIMARY KEY,
        id_nguoi_dung INTEGER,
        ngay_dat DATETIME,
        trang_thai TEXT,
        tong_tien REAL,
        FOREIGN KEY (id_nguoi_dung) REFERENCES NguoiDung(id)
    );

    CREATE TABLE IF NOT EXISTS ChiTietDonHang (
        id INTEGER PRIMARY KEY,
        id_don_hang INTEGER,
        id_bien_the INTEGER,
        so_luong INTEGER,
        FOREIGN KEY (id_don_hang) REFERENCES DonHang(id),
        FOREIGN KEY (id_bien_the) REFERENCES BienTheSanPham(id)
    );

    CREATE TABLE IF NOT EXISTS ThanhToan (
        id INTEGER PRIMARY KEY,
        id_nguoi_dung INTEGER,
        loai_the TEXT,
        so_the TEXT,
        dia_chi_giao_hang TEXT,
        FOREIGN KEY (id_nguoi_dung) REFERENCES NguoiDung(id)
    );

    CREATE TABLE IF NOT EXISTS DanhGiaSanPham (
        id INTEGER PRIMARY KEY,
        id_san_pham INTEGER,
        id_nguoi_dung INTEGER,
        noi_dung TEXT,
        ngay_danh_gia DATE,
        FOREIGN KEY (id_san_pham) REFERENCES SanPham(id),
        FOREIGN KEY (id_nguoi_dung) REFERENCES NguoiDung(id)
    );

    CREATE TABLE IF NOT EXISTS GoiYSanPham (
        id INTEGER PRIMARY KEY,
        id_san_pham_nguon INTEGER,
        id_san_pham_goi_y INTEGER,
        FOREIGN KEY (id_san_pham_nguon) REFERENCES SanPham(id),
        FOREIGN KEY (id_san_pham_goi_y) REFERENCES SanPham(id)
    );

    CREATE TABLE IF NOT EXISTS CustomOrder (
        id INTEGER PRIMARY KEY,
        id_nguoi_dung INTEGER,
        mo_ta_yeu_cau TEXT,
        ngay_dat DATETIME,
        trang_thai TEXT,
        FOREIGN KEY (id_nguoi_dung) REFERENCES NguoiDung(id)
    );

    CREATE TABLE IF NOT EXISTS DonHoTro (
        id INTEGER PRIMARY KEY,
        id_nguoi_dung INTEGER,
        noi_dung TEXT,
        ngay_gui DATETIME,
        trang_thai TEXT,
        FOREIGN KEY (id_nguoi_dung) REFERENCES NguoiDung(id)
    );

    CREATE TABLE IF NOT EXISTS MaGiamGia (
        id INTEGER PRIMARY KEY,
        ma TEXT,
        dieu_kien TEXT,
        han_su_dung DATE
    );
    """)
    conn.commit()
    conn.close()
    return '✅ Tất cả bảng đã được tạo thành công!'



# -----------------------------------------------------------------------INSERT SAMPLE DATA------------------------------------------------------------------- #
# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# # Enable foreign key constraints
# cursor.execute('PRAGMA foreign_keys = ON;')

# # --- Minimal Product-Related Data (to satisfy foreign key constraints) ---
# # Insert a dummy category
# cursor.execute('INSERT INTO DanhMucSanPham (ten_danh_muc) VALUES (?)', ('Đồ bơi nữ',))

# # Insert a dummy product
# cursor.execute('INSERT INTO SanPham (ten_san_pham, mo_ta, gia_ban, id_danh_muc, hinh_anh_chinh) VALUES (?, ?, ?, ?, ?)',
#                ('Đồ bơi nữ mẫu 1', 'Mô tả sản phẩm', 250000.0, 1, 'do_boi_nu.jpg'))

# # Insert a dummy size
# cursor.execute('INSERT INTO KichCo (ten_kich_co) VALUES (?)', ('M',))

# # Insert a dummy color
# cursor.execute('INSERT INTO MauSac (ten_mau) VALUES (?)', ('Trắng',))

# # Insert a dummy product variant
# cursor.execute('INSERT INTO BienTheSanPham (id_san_pham, id_kich_co, id_mau_sac, so_luong_ton) VALUES (?, ?, ?, ?)',
#                (1, 1, 1, 10))

# --- Insert Sample Data into Non-Product Tables ---

# # 1. NguoiDung (Users)
# # Hash passwords using bcrypt
# password1 = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
# password2 = bcrypt.hashpw('secure456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# cursor.executemany('INSERT INTO NguoiDung (ten_nguoi_dung, email, ngay_tao_tai_khoan, mat_khau) VALUES (?, ?, ?, ?)',
#                    [
#                        ('Nguyen Van A', 'a@example.com', '2024-01-15', password1),
#                        ('Tran Thi B', 'b@example.com', '2024-03-20', password2),
#                    ])

# # 2. Banner
# cursor.executemany('INSERT INTO Banner (hinh_anh, vi_tri) VALUES (?, ?)',
#                    [
#                        ('banner1.jpg', 'Top'),
#                        ('banner2.jpg', 'Middle'),
#                        ('banner3.jpg', 'Bottom'),
#                    ])

# # 3. GioHang (Cart) - References a product variant and user
# cursor.executemany('INSERT INTO GioHang (id_nguoi_dung, id_bien_the, so_luong) VALUES (?, ?, ?)',
#                    [
#                        (1, 1, 2),  # User 1 has 2 items of variant 1
#                        (2, 1, 1),  # User 2 has 1 item of variant 1
#                    ])

# # 4. DonHang (Orders)
# cursor.executemany('INSERT INTO DonHang (id_nguoi_dung, ngay_dat, trang_thai, tong_tien) VALUES (?, ?, ?, ?)',
#                    [
#                        (1, '2025-05-01 10:00:00', 'Đã giao', 500000.0),
#                        (1, '2025-05-15 14:30:00', 'Đang xử lý', 300000.0),
#                        (2, '2025-05-20 09:15:00', 'Đã hủy', 200000.0),
#                    ])

# # 5. ChiTietDonHang (Order Details) - References orders and product variants
# cursor.executemany('INSERT INTO ChiTietDonHang (id_don_hang, id_bien_the, so_luong) VALUES (?, ?, ?)',
#                    [
#                        (1, 1, 2),  # Order 1 has 2 items of variant 1
#                        (2, 1, 1),  # Order 2 has 1 item of variant 1
#                        (3, 1, 1),  # Order 3 has 1 item of variant 1
#                    ])

# # 6. ThanhToan (Payment)
# cursor.executemany('INSERT INTO ThanhToan (id_nguoi_dung, loai_the, so_the, dia_chi_giao_hang) VALUES (?, ?, ?, ?)',
#                    [
#                        (1, 'Visa', '1234-5678-9012-3456', '123 Đường ABC, TP.HCM'),
#                        (2, 'MasterCard', '9876-5432-1098-7654', '456 Đường XYZ, Hà Nội'),
#                    ])

# # 7. DanhGiaSanPham (Product Reviews) - References a product and user
# cursor.executemany('INSERT INTO DanhGiaSanPham (id_san_pham, id_nguoi_dung, noi_dung, ngay_danh_gia) VALUES (?, ?, ?, ?)',
#                    [
#                        (1, 1, 'Sản phẩm rất đẹp, chất lượng tốt!', '2025-05-02'),
#                        (1, 2, 'Hơi chật, nhưng màu sắc rất ưng ý.', '2025-05-21'),
#                    ])

# # 8. GoiYSanPham (Product Recommendations) - References two products
# cursor.execute('INSERT INTO GoiYSanPham (id_san_pham_nguon, id_san_pham_goi_y) VALUES (?, ?)',
#                (1, 1))  # Dummy self-reference since we only have 1 product

# # 9. CustomOrder (Custom Orders)
# cursor.executemany('INSERT INTO CustomOrder (id_nguoi_dung, mo_ta_yeu_cau, ngay_dat, trang_thai) VALUES (?, ?, ?, ?)',
#                    [
#                        (1, 'Tôi muốn một bộ đồ bơi màu hồng, size L', '2025-05-10 08:00:00', 'Đang xử lý'),
#                        (2, 'Thiết kế đồ bơi trẻ em, màu xanh dương', '2025-05-22 16:00:00', 'Đã hoàn thành'),
#                    ])

# # 10. DonHoTro (Support Tickets)
# cursor.executemany('INSERT INTO DonHoTro (id_nguoi_dung, noi_dung, ngay_gui, trang_thai) VALUES (?, ?, ?, ?)',
#                    [
#                        (1, 'Tôi muốn đổi size đồ bơi đã mua', '2025-05-03 12:00:00', 'Đã giải quyết'),
#                        (2, 'Giao hàng trễ, vui lòng kiểm tra', '2025-05-23 10:30:00', 'Đang xử lý'),
#                    ])

# # 11. MaGiamGia (Discount Codes)
# cursor.executemany('INSERT INTO MaGiamGia (ma, dieu_kien, han_su_dung) VALUES (?, ?, ?)',
#                    [
#                        ('GIAM10', 'Giảm 10% cho đơn hàng từ 500k', '2025-12-31'),
#                        ('FREESHIP', 'Miễn phí vận chuyển cho đơn hàng từ 300k', '2025-06-30'),
#                    ])

# # Commit changes and close connection
# conn.commit()
conn.close()

# print("Sample data inserted successfully!")


