from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = '******'

# DATABASE CONNECTION #
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn





# WEBSITE BACKEND FUNCTIONS #

# Signup route (for user to create new account)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    success = None

    if request.method == 'POST':
        ten_nguoi_dung = request.form['ten_nguoi_dung']
        email = request.form['email']
        mat_khau = request.form['mat_khau'].encode('utf-8')  # Encode the password

        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(mat_khau, bcrypt.gensalt())

        conn = sqlite3.connect('database.db')  # Replace with your database name
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM NguoiDung WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = 'Email này đã được đăng ký.'
        else:
            cursor.execute(
                "INSERT INTO NguoiDung (ten_nguoi_dung, email, mat_khau) VALUES (?, ?, ?)",
                (ten_nguoi_dung, email, hashed_password)
            )
            conn.commit()
            success = 'Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.'
        
        conn.close()

    return render_template('signup.html', error=error, success=success)

# Login route (for user authentication)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM NguoiDung WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user['mat_khau'].encode('utf-8')):
            session['user_id'] = user['id']
            return redirect(url_for('account'))
        return render_template('login.html', error='Email hoặc mật khẩu không đúng!')
    return render_template('login.html')

# Homepage route
@app.route('/')
def get_all_products():
    conn = get_db_connection()
    query = """
        SELECT SanPham.ten_san_pham, SanPham.gia_ban, KichCo.ten_kich_co, 
               MauSac.ten_mau, BienTheSanPham.hinh_anh
        FROM SanPham
        JOIN BienTheSanPham ON SanPham.id = BienTheSanPham.id_san_pham
        JOIN KichCo ON BienTheSanPham.id_kich_co = KichCo.id
        JOIN MauSac ON BienTheSanPham.id_mau_sac = MauSac.id
        JOIN DanhMucSanPham ON SanPham.id_danh_muc = DanhMucSanPham.id
    """
    products = conn.execute(query).fetchall()
    conn.close()
    return render_template('homepage.html', products=products)

@app.route('/api/homepage')
def filter_products():
    size = request.args.get('size')
    color = request.args.get('color')
    category = request.args.get('category')

    query = """
        SELECT BienTheSanPham.id, BienTheSanPham.hinh_anh, SanPham.ten_san_pham, SanPham.gia_ban, 
                KichCo.ten_kich_co, MauSac.ten_mau, DanhMucSanPham.ten_danh_muc
        FROM BienTheSanPham
        JOIN SanPham ON BienTheSanPham.id_san_pham = SanPham.id
        JOIN KichCo ON BienTheSanPham.id_kich_co = KichCo.id
        JOIN MauSac ON BienTheSanPham.id_mau_sac = MauSac.id
        JOIN DanhMucSanPham ON SanPham.id_danh_muc = DanhMucSanPham.id
        WHERE 1=1
    """
    params = []

    if size:
        query += " AND KichCo.ten_kich_co = ?"
        params.append(size)
    if color:
        query += " AND MauSac.ten_mau = ?"
        params.append(color)
    if category:
        query += " AND DanhMucSanPham.ten_danh_muc = ?"
        params.append(category)

    conn = get_db_connection()
    products = conn.execute(query, params).fetchall()
    # print([dict(row) for row in products])  # Debug print
    conn.close()

    return jsonify([dict(row) for row in products])

# Custompage route
@app.route('/custompage')
def custom_page():
    return render_template('custompage.html')

# New checkout route
@app.route('/checkout')
def checkout():
    # if 'user_id' not in session:
    #     return redirect(url_for('login'))  # Redirect to login if not authenticated
    # user_id = session['user_id']
    # conn = get_db_connection()
    # # Fetch cart or order data for the user (example)
    # cart = conn.execute('SELECT * FROM GioHang WHERE id_nguoi_dung = ?', (user_id,)).fetchall()
    # conn.close()
    return render_template('checkout.html') #cart=cart#

# Lookbook route
@app.route('/lookbook')
def lookbook():
    return render_template('lookbook.html')

# Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Cart route
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Account route
@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user_id = session['user_id']
    conn = get_db_connection()

    # Fetch user info
    user = conn.execute('SELECT ten_nguoi_dung, email, ngay_tao_tai_khoan FROM NguoiDung WHERE id = ?', 
                        (user_id,)).fetchone()

    # Fetch order history with product details
    orders = conn.execute('''
        SELECT dh.id, dh.ngay_dat, dh.trang_thai, dh.tong_tien, 
               sp.ten_san_pham, kc.ten_kich_co, ms.ten_mau, ctdh.so_luong
        FROM DonHang dh
        LEFT JOIN ChiTietDonHang ctdh ON dh.id = ctdh.id_don_hang
        LEFT JOIN BienTheSanPham btsp ON ctdh.id_bien_the = btsp.id
        LEFT JOIN SanPham sp ON btsp.id_san_pham = sp.id
        LEFT JOIN KichCo kc ON btsp.id_kich_co = kc.id
        LEFT JOIN MauSac ms ON btsp.id_mau_sac = ms.id
        WHERE dh.id_nguoi_dung = ?
        ORDER BY dh.ngay_dat DESC
    ''', (user_id,)).fetchall()

    # Fetch payment info
    payment = conn.execute('SELECT loai_the, so_the, dia_chi_giao_hang FROM ThanhToan WHERE id_nguoi_dung = ?', 
                           (user_id,)).fetchone()
    
    # Handle profile update or logout
    if request.method == 'POST':
        if 'logout' in request.form:  # Check if logout button was clicked
            session.pop('user_id', None)
            return redirect(url_for('login'))  # Redirect to login page after logout
        else:  # Handle profile update
            new_name = request.form['name']
            new_email = request.form['email']
            old_password = request.form['old_password'].encode('utf-8')
            new_password = request.form['new_password'].encode('utf-8')

            # Verify old password
            stored_password = conn.execute('SELECT mat_khau FROM NguoiDung WHERE id = ?', 
                                           (user_id,)).fetchone()['mat_khau']
            if not bcrypt.checkpw(old_password, stored_password):
                conn.close()
                return render_template('account.html', user=user, orders=orders, payment=payment, 
                                     error="Mật khẩu cũ không đúng!")

            # Update user profile
            hashed_new_password = bcrypt.hashpw(new_password, bcrypt.gensalt()).decode('utf-8')
            conn.execute('UPDATE NguoiDung SET ten_nguoi_dung = ?, email = ?, mat_khau = ? WHERE id = ?', 
                         (new_name, new_email, hashed_new_password, user_id))
            conn.commit()
            conn.close()
            return redirect(url_for('account'))

    conn.close()
    return render_template('account.html', user=user, orders=orders, payment=payment)

# Language route
@app.route('/language')
def language():
    return render_template('language.html')

if __name__ == '__main__':
    app.run(debug=True)