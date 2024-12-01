import mysql.connector
from flask import Flask
import hashlib
from models import NguoiDung


def authenticate_user(email, password):
    """Xác thực người dùng dựa trên email và mật khẩu."""
    # Tìm người dùng qua email
    user = NguoiDung.query.filter_by(email=email).first()

    # Kiểm tra người dùng và so khớp mật khẩu
    if user:
        hashed_password = hashlib.md5(password.encode()).hexdigest()  # Mã hóa mật khẩu nhập vào
        if user.mat_khau == hashed_password:  # So sánh mật khẩu đã mã hóa
            return user
    return None