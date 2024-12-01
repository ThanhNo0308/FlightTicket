from flask import Blueprint, render_template, redirect, url_for, flash, session, request
# from db_utils import cursor, db
from extensions import db
from models import LichChuyenBay, SanBay, QuyDinh, SanBayTrungGian

lich_chuyen_bay_routes = Blueprint('lich_chuyen_bay_routes', __name__)


@lich_chuyen_bay_routes.route('/lich_chuyen_bay/<ma_chuyen_bay>', methods=['GET', 'POST'])
def lich_chuyen_bay(ma_chuyen_bay):
    try:
        # Lấy danh sách lịch chuyến bay
        lich_chuyen_bay_list = LichChuyenBay.query.filter_by(ma_chuyen_bay=ma_chuyen_bay).all()

        # Lấy quyền của người dùng
        quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')

        # Nếu danh sách rỗng, nhưng vẫn cho phép truy cập
        if not lich_chuyen_bay_list:
            flash('Không tìm thấy lịch chuyến bay!')

        # Kiểm tra quyền để điều hướng hiển thị
        if quyen == "Người quản trị":
            return render_template(
                'lich_chuyen_bay_admin.html',  # Hiển thị giao diện admin
                lich_chuyen_bay_list=lich_chuyen_bay_list,
                ma_chuyen_bay=ma_chuyen_bay,
                quyen=quyen
            )
        elif quyen == "Nhân viên":
            return render_template(
                'lich_chuyen_bay.html',  # Hiển thị giao diện nhân viên
                lich_chuyen_bay_list=lich_chuyen_bay_list,
                ma_chuyen_bay=ma_chuyen_bay,
                quyen=quyen
            )
        else:
            flash('Bạn không có quyền truy cập!')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))

    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}')
        return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))







@lich_chuyen_bay_routes.route('/them_lich_chuyen_bay/<ma_chuyen_bay>', methods=['GET', 'POST'])
def them_lich_chuyen_bay(ma_chuyen_bay):
    quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')

    # Kiểm tra quyền: chỉ "Người quản trị" hoặc "Nhân viên" được truy cập
    if quyen not in ['Người quản trị', 'Nhân viên']:
        flash('Bạn không có quyền truy cập!')
        return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))

    if request.method == 'POST':
        # Lấy thông tin từ form
        ngay_gio_khoi_hanh = request.form.get('ngay_gio_khoi_hanh')
        thoi_gian_bay_phut = request.form.get('thoi_gian_bay_phut')
        so_ghe_hang_1 = request.form.get('so_ghe_hang_1')
        so_ghe_hang_2 = request.form.get('so_ghe_hang_2')

        try:
            # Tạo đối tượng LichChuyenBay và thêm vào cơ sở dữ liệu
            lich_chuyen_bay = LichChuyenBay(
                ma_chuyen_bay=ma_chuyen_bay,
                ngay_gio_khoi_hanh=ngay_gio_khoi_hanh,
                thoi_gian_bay_phut=thoi_gian_bay_phut,
                so_ghe_hang_1=so_ghe_hang_1,
                so_ghe_hang_2=so_ghe_hang_2
            )
            db.session.add(lich_chuyen_bay)
            db.session.commit()

            # Lấy ID của lịch chuyến bay vừa thêm
            last_insert_id = lich_chuyen_bay.ma_lich_chuyen_bay

            # Thêm các sân bay trung gian
            stt_list = request.form.getlist('stt[]')
            san_bay_trung_gian_list = request.form.getlist('san_bay_trung_gian[]')
            thoi_gian_dung_phut_list = request.form.getlist('thoi_gian_dung_phut[]')
            ghi_chu_list = request.form.getlist('ghi_chu[]')

            for stt, san_bay, thoi_gian, ghi_chu in zip(stt_list, san_bay_trung_gian_list, thoi_gian_dung_phut_list, ghi_chu_list):
                san_bay_trung_gian = SanBayTrungGian(
                    stt=stt,
                    ma_lich_chuyen_bay=last_insert_id,
                    san_bay_trung_gian=san_bay,
                    thoi_gian_dung_phut=thoi_gian,
                    ghi_chu=ghi_chu
                )
                db.session.add(san_bay_trung_gian)

            db.session.commit()
            flash('Thêm lịch chuyến bay thành công!')
            return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}')

    try:
        # Truy vấn danh sách sân bay để hiển thị trong dropdown
        danh_sach_san_bay = SanBay.query.all()
        # Truy vấn thông tin quy định
        quy_dinh_info = QuyDinh.query.first()

        # Render trang dựa trên quyền
        if quyen == 'Người quản trị':
            return render_template('them_lich_chuyen_bay_admin.html', 
                                   ma_chuyen_bay=ma_chuyen_bay, 
                                   danh_sach_san_bay=danh_sach_san_bay, 
                                   quy_dinh_info=quy_dinh_info, 
                                   quyen=quyen)
        elif quyen == 'Nhân viên':
            return render_template('them_lich_chuyen_bay.html', 
                                   ma_chuyen_bay=ma_chuyen_bay, 
                                   danh_sach_san_bay=danh_sach_san_bay, 
                                   quy_dinh_info=quy_dinh_info, 
                                   quyen=quyen)

    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}')
        return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))




@lich_chuyen_bay_routes.route('/sua_lich_chuyen_bay/<int:ma_lich_chuyen_bay>', methods=['GET', 'POST'])
def sua_lich_chuyen_bay(ma_lich_chuyen_bay):
    try:
        # Lấy thông tin lịch chuyến bay hiện tại
        lich_chuyen_bay = LichChuyenBay.query.get_or_404(ma_lich_chuyen_bay)
        ma_chuyen_bay = lich_chuyen_bay.ma_chuyen_bay

        if request.method == 'POST':
            # Lấy dữ liệu từ form
            lich_chuyen_bay.ngay_gio_khoi_hanh = request.form.get('ngay_gio_khoi_hanh')
            lich_chuyen_bay.thoi_gian_bay_phut = request.form.get('thoi_gian_bay_phut')
            lich_chuyen_bay.so_ghe_hang_1 = request.form.get('so_ghe_hang_1')
            lich_chuyen_bay.so_ghe_hang_2 = request.form.get('so_ghe_hang_2')

            # Xóa các sân bay trung gian cũ
            SanBayTrungGian.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay).delete()

            # Thêm các sân bay trung gian mới
            stt_list = request.form.getlist('stt[]')
            san_bay_trung_gian_list = request.form.getlist('san_bay_trung_gian[]')
            thoi_gian_dung_phut_list = request.form.getlist('thoi_gian_dung_phut[]')
            ghi_chu_list = request.form.getlist('ghi_chu[]')

            for stt, san_bay, thoi_gian, ghi_chu in zip(stt_list, san_bay_trung_gian_list, thoi_gian_dung_phut_list, ghi_chu_list):
                san_bay_trung_gian = SanBayTrungGian(
                    stt=stt,
                    ma_lich_chuyen_bay=ma_lich_chuyen_bay,
                    san_bay_trung_gian=san_bay,
                    thoi_gian_dung_phut=thoi_gian,
                    ghi_chu=ghi_chu
                )
                db.session.add(san_bay_trung_gian)

            db.session.commit()

            # Điều hướng dựa trên quyền
            quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
            flash('Cập nhật lịch chuyến bay thành công!')
            if quyen == "Người quản trị":
                return redirect(url_for('lich_chuyen_bay_routes.danh_sach_lich_chuyen_bay_admin'))
            elif quyen == "Nhân viên":
                return redirect(url_for('lich_chuyen_bay_routes.danh_sach_lich_chuyen_bay'))

        # Truy vấn danh sách sân bay và quy định
        danh_sach_san_bay = SanBay.query.all()
        danh_sach_san_bay_trung_gian = SanBayTrungGian.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay).all()
        quy_dinh_info = QuyDinh.query.first()
        quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')

        if quyen == 'Người quản trị':
            return render_template('sua_lich_chuyen_bay_admin.html', 
                                  lich_chuyen_bay=lich_chuyen_bay,
            danh_sach_san_bay_trung_gian=danh_sach_san_bay_trung_gian,
            danh_sach_san_bay=danh_sach_san_bay,
            quy_dinh_info=quy_dinh_info,
            quyen=quyen)
        elif quyen == 'Nhân viên':
            return render_template('sua_lich_chuyen_bay.html', 
                                   lich_chuyen_bay=lich_chuyen_bay,
            danh_sach_san_bay_trung_gian=danh_sach_san_bay_trung_gian,
            danh_sach_san_bay=danh_sach_san_bay,
            quy_dinh_info=quy_dinh_info,
            quyen=quyen)
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}')
        return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))




@lich_chuyen_bay_routes.route('/xoa_lich_chuyen_bay/<int:ma_lich_chuyen_bay>')
def xoa_lich_chuyen_bay(ma_lich_chuyen_bay):
    try:
        # Lấy thông tin lịch chuyến bay
        lich_chuyen_bay = LichChuyenBay.query.get_or_404(ma_lich_chuyen_bay)
        ma_chuyen_bay = lich_chuyen_bay.ma_chuyen_bay

        # Xóa lịch chuyến bay và các sân bay trung gian liên quan
        SanBayTrungGian.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay).delete()
        db.session.delete(lich_chuyen_bay)
        db.session.commit()

        flash('Xóa lịch chuyến bay thành công!')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}')

    return redirect(url_for('lich_chuyen_bay_routes.lich_chuyen_bay', ma_chuyen_bay=ma_chuyen_bay))


