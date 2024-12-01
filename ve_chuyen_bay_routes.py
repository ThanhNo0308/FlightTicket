from flask import Blueprint, render_template, redirect, url_for, flash, session, request
# from db_utils import cursor, db
from extensions import db
from datetime import datetime, timedelta
import vnpay
from models import VeChuyenBay

ve_chuyen_bay_routes = Blueprint('ve_chuyen_bay_routes', __name__)


@ve_chuyen_bay_routes.route('/ve_chuyen_bay/<ma_chuyen_bay>', methods=['GET'])
def ve_chuyen_bay(ma_chuyen_bay):
    try:
        # Truy vấn danh sách vé chuyến bay theo mã chuyến bay
        ve_chuyen_bay_list = VeChuyenBay.query.filter_by(ma_chuyen_bay=ma_chuyen_bay).all()
        quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
        return render_template('ve_chuyen_bay.html', ve_chuyen_bay_list=ve_chuyen_bay_list, ma_chuyen_bay=ma_chuyen_bay,
                               quyen=quyen)
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}')
        return redirect(url_for('home'))  


@ve_chuyen_bay_routes.route('/sua_ve_chuyen_bay/<ma_ve>', methods=['GET', 'POST'])
def sua_ve_chuyen_bay(ma_ve):
    if request.method == 'GET':
        try:
            # Truy vấn thông tin vé chuyến bay theo mã vé
            flight_ticket = VeChuyenBay.query.filter_by(ma_ve=ma_ve).first()
            quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
            if flight_ticket:
                return render_template('sua_ve_chuyen_bay.html', flight_ticket=flight_ticket, quyen=quyen)
            else:
                flash('Vé chuyến bay không tồn tại!')
                return redirect(url_for('ve_chuyen_bay_routes.ve_chuyen_bay', ma_chuyen_bay=ma_ve))
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}')
            return redirect(url_for('home'))  # Hoặc trang phù hợp trong ứng dụng của bạn

    elif request.method == 'POST':
        try:
            # Lấy thông tin từ form
            hang_ve_moi = request.form['hang_ve']
            gia_moi = int(request.form['gia'])

            # Truy vấn và cập nhật thông tin vé chuyến bay
            flight_ticket = VeChuyenBay.query.filter_by(ma_ve=ma_ve).first()
            if flight_ticket:
                flight_ticket.hang_ve = hang_ve_moi
                flight_ticket.gia = gia_moi

                # Lưu thay đổi vào cơ sở dữ liệu
                db.session.commit()

                flash('Cập nhật vé chuyến bay thành công!')
                return redirect(url_for('ve_chuyen_bay_routes.ve_chuyen_bay', ma_chuyen_bay=flight_ticket.ma_chuyen_bay))
            else:
                flash('Vé chuyến bay không tồn tại!')
                return redirect(url_for('ve_chuyen_bay_routes.ve_chuyen_bay', ma_chuyen_bay=ma_ve))
        except Exception as e:
            # Xử lý lỗi nếu có
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}')
            return redirect(url_for('ve_chuyen_bay_routes.ve_chuyen_bay', ma_chuyen_bay=ma_ve))
