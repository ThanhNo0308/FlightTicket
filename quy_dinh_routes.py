from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
# from db_utils import cursor, db
from extensions import db
from datetime import datetime, timedelta
import vnpay
from models import ChuyenBay, VeChuyenBay, DatVeChuyenBay, QuyDinh
from sqlalchemy import extract, func

quy_dinh_routes = Blueprint('quy_dinh_routes', __name__)


@quy_dinh_routes.route('/doanh_thu_theo_thang', methods=['GET', 'POST'])
def doanh_thu_theo_thang():
    if request.method == 'POST':
        # Lấy tháng từ yêu cầu POST
        selected_month = int(request.form['selected_month'].split("-")[1])
    else:
        quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
        # Lấy tháng từ yêu cầu GET hoặc thiết lập giá trị mặc định
        return render_template('doanh_thu_theo_thang.html', quyen=quyen)

    try:
        # Thực hiện truy vấn SQLAlchemy để lấy dữ liệu doanh thu theo tháng
        result = db.session.query(
            ChuyenBay.san_bay_di,
            ChuyenBay.san_bay_den,
            func.sum(VeChuyenBay.gia).label('doanh_thu'),
            func.count(VeChuyenBay.ma_ve).label('so_luot_bay')
        ).join(
            VeChuyenBay, VeChuyenBay.ma_chuyen_bay == ChuyenBay.ma_chuyen_bay
        ).join(
            DatVeChuyenBay, VeChuyenBay.ma_ve == DatVeChuyenBay.ma_ve
        ).filter(
            extract('month', DatVeChuyenBay.thoi_diem_dat_ve) == selected_month
        ).group_by(
            ChuyenBay.san_bay_di, ChuyenBay.san_bay_den
        ).all()

        # Chuẩn bị dữ liệu cho biểu đồ
        labels = [f"{row.san_bay_di} - {row.san_bay_den}" for row in result]
        data = [row.doanh_thu for row in result]

        # Tính tổng doanh thu
        total_revenue = sum(data)

        # Tính tỷ lệ doanh thu
        percentages = [(revenue / total_revenue) * 100 for revenue in data]

        # Chuẩn bị dữ liệu để trả về dưới dạng JSON
        chart_data = {
            'labels': labels,
            'data': data,
            'percentages': percentages,
            'total_revenue': total_revenue
        }

        return jsonify(chart_data)

    except Exception as e:
        # Handle the exception, e.g., log it or return an error response
        return jsonify({'error': str(e)})


@quy_dinh_routes.route('/thay_doi_quy_dinh', methods=['GET', 'POST'])
def thay_doi_quy_dinh():
    if request.method == 'GET':
        try:
            # Lấy thông tin quy định hiện tại từ cơ sở dữ liệu
            quy_dinh = QuyDinh.query.first()  # Giả định chỉ có 1 bản ghi quy định trong bảng
            quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
            return render_template('thay_doi_quy_dinh.html', quy_dinh=quy_dinh, quyen=quyen)
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}')
            return redirect(url_for('quy_dinh_routes.thay_doi_quy_dinh'))

    elif request.method == 'POST':
        try:
            # Lấy thông tin từ form
            so_luong_san_bay = int(request.form['so_luong_san_bay'])
            thoi_gian_bay_toi_thieu = int(request.form['thoi_gian_bay_toi_thieu'])
            so_san_bay_trung_gian_toi_da = int(request.form['so_san_bay_trung_gian_toi_da'])
            thoi_gian_dung_toi_thieu = int(request.form['thoi_gian_dung_toi_thieu'])
            thoi_gian_dung_toi_da = int(request.form['thoi_gian_dung_toi_da'])
            so_gio_dat_ve_truoc = int(request.form['so_gio_dat_ve_truoc'])
            so_gio_ban_ve_truoc = int(request.form['so_gio_ban_ve_truoc'])

            # Lấy bản ghi đầu tiên trong bảng quy định
            quy_dinh = QuyDinh.query.first()
            if not quy_dinh:
                flash('Không tìm thấy quy định để cập nhật!')
                return redirect(url_for('quy_dinh_routes.thay_doi_quy_dinh'))

            # Cập nhật thông tin trong bản ghi quy định
            quy_dinh.so_luong_san_bay = so_luong_san_bay
            quy_dinh.thoi_gian_bay_toi_thieu = thoi_gian_bay_toi_thieu
            quy_dinh.so_san_bay_trung_gian_toi_da = so_san_bay_trung_gian_toi_da
            quy_dinh.thoi_gian_dung_toi_thieu = thoi_gian_dung_toi_thieu
            quy_dinh.thoi_gian_dung_toi_da = thoi_gian_dung_toi_da
            quy_dinh.so_gio_dat_ve_truoc = so_gio_dat_ve_truoc
            quy_dinh.so_gio_ban_ve_truoc = so_gio_ban_ve_truoc

            # Lưu thay đổi vào cơ sở dữ liệu
            db.session.commit()

            flash('Cập nhật quy định thành công!')
            return redirect(url_for('quy_dinh_routes.thay_doi_quy_dinh'))

        except Exception as e:
            # Xử lý lỗi, ví dụ: log lỗi hoặc trả về một trang lỗi
            db.session.rollback()  # Quay lại nếu có lỗi xảy ra
            flash(f'Có lỗi xảy ra: {str(e)}')
            return redirect(url_for('quy_dinh_routes.thay_doi_quy_dinh'))

