from flask import Blueprint, request, jsonify, render_template
import hashlib
from extensions import db
from models import NguoiDung  # Import model User đã định nghĩa trong models.py

# Khởi tạo Blueprint cho register
register_bp = Blueprint('register', __name__)

# Route đăng ký
@register_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@register_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    # Kiểm tra email đã tồn tại trong cơ sở dữ liệu
    user = NguoiDung.query.filter_by(email=email).first()
    if user:
        return jsonify({'success': False, 'message': 'Email này đã được sử dụng!'})

    # Mã hóa mật khẩu
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    # Thêm người dùng mới vào cơ sở dữ liệu
    new_user = NguoiDung(
        ten_nguoi_dung=fullname,
        email=email,
        phone=phone,
        mat_khau=hashed_password,
        vai_tro='Khách hàng'
    )
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Đăng ký thành công!'})
