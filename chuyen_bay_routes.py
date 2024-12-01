from flask import Blueprint, render_template, redirect, url_for, flash, session, request
# from db_utils import cursor, db
from extensions import db
from models import ChuyenBay, SanBay, VeChuyenBay
from sqlalchemy.orm import joinedload

chuyen_bay_routes = Blueprint('chuyen_bay_routes', __name__)


@chuyen_bay_routes.route('/them_chuyen_bay', methods=['GET', 'POST'])
def them_chuyen_bay():
    if request.method == 'GET':
        try:
            # Lấy danh sách sân bay từ cơ sở dữ liệu
            danh_sach_san_bay = SanBay.query.all()
            quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
            return render_template('them_chuyen_bay.html', danh_sach_san_bay=danh_sach_san_bay, quyen=quyen)
        except Exception as e:
            flash(f'Có lỗi xảy ra khi tải danh sách sân bay: {str(e)}')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay_admin'))

    elif request.method == 'POST':
        # Lấy thông tin từ form
        ma_chuyen_bay = request.form.get('ma_chuyen_bay')
        san_bay_di = request.form.get('san_bay_di')
        san_bay_den = request.form.get('san_bay_den')


        try:
            # Tạo đối tượng ChuyenBay
            chuyen_bay = ChuyenBay(
                ma_chuyen_bay=ma_chuyen_bay,
                san_bay_di=san_bay_di,
                san_bay_den=san_bay_den
            )
            db.session.add(chuyen_bay)

            # Thêm vé Hạng 1
            ve_hang_1 = VeChuyenBay(
                ma_chuyen_bay=ma_chuyen_bay,
                hang_ve='Hạng 1',
                gia=1500000
            )
            db.session.add(ve_hang_1)

            # Thêm vé Hạng 2
            ve_hang_2 = VeChuyenBay(
                ma_chuyen_bay=ma_chuyen_bay,
                hang_ve='Hạng 2',
                gia=800000
            )
            db.session.add(ve_hang_2)

            # Lưu thay đổi vào cơ sở dữ liệu
            db.session.commit()

            flash('Thêm chuyến bay thành công!')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay_admin'))

        except Exception as e:
            # Rollback nếu có lỗi
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}')

    quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
    return render_template('them_chuyen_bay.html', quyen=quyen)


@chuyen_bay_routes.route('/sua_chuyen_bay/<ma_chuyen_bay>', methods=['GET', 'POST'])
def sua_chuyen_bay(ma_chuyen_bay):
    if request.method == 'GET':
        try:
            # Lấy thông tin chuyến bay từ cơ sở dữ liệu
            chuyen_bay = ChuyenBay.query.filter_by(ma_chuyen_bay=ma_chuyen_bay).first()

            if chuyen_bay:
                # Lấy danh sách sân bay
                danh_sach_san_bay = SanBay.query.all()
                quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
                return render_template('sua_chuyen_bay.html', chuyen_bay=chuyen_bay, danh_sach_san_bay=danh_sach_san_bay, quyen=quyen)
            else:
                flash('Chuyến bay không tồn tại!')
                return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))

        except Exception as e:
            flash(f'Có lỗi xảy ra khi tải thông tin chuyến bay: {str(e)}')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))

    elif request.method == 'POST':
        # Lấy thông tin từ form
        san_bay_di_moi = request.form.get('san_bay_di')
        san_bay_den_moi = request.form.get('san_bay_den')

        try:
            # Lấy chuyến bay cần sửa
            chuyen_bay = ChuyenBay.query.filter_by(ma_chuyen_bay=ma_chuyen_bay).first()

            if not chuyen_bay:
                flash('Chuyến bay không tồn tại!')
                return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))

            # Cập nhật thông tin chuyến bay
            chuyen_bay.san_bay_di = san_bay_di_moi
            chuyen_bay.san_bay_den = san_bay_den_moi

            # Lưu thay đổi vào cơ sở dữ liệu
            db.session.commit()

            flash('Cập nhật chuyến bay thành công!')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay_admin'))

        except Exception as e:
            # Rollback nếu có lỗi
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))


@chuyen_bay_routes.route('/xoa_chuyen_bay/<ma_chuyen_bay>')
def xoa_chuyen_bay(ma_chuyen_bay):
    try:
        # Lấy chuyến bay cần xóa
        chuyen_bay = ChuyenBay.query.filter_by(ma_chuyen_bay=ma_chuyen_bay).first()

        if not chuyen_bay:
            flash('Chuyến bay không tồn tại!')
            return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay'))

        # Xóa chuyến bay
        db.session.delete(chuyen_bay)
        db.session.commit()

        flash('Xóa chuyến bay thành công!')
    except Exception as e:
        # Rollback nếu có lỗi
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}')

    return redirect(url_for('chuyen_bay_routes.danh_sach_chuyen_bay_admin'))


@chuyen_bay_routes.route('/danh_sach_chuyen_bay')
def danh_sach_chuyen_bay():
    try:
        # Lấy danh sách chuyến bay từ cơ sở dữ liệu
        chuyen_bay_list = ChuyenBay.query.all()
        quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
        return render_template('danh_sach_chuyen_bay.html', chuyen_bay_list=chuyen_bay_list, quyen=quyen)
    except Exception as e:
        flash(f'Có lỗi xảy ra khi tải danh sách chuyến bay: {str(e)}')
        return redirect(url_for('chuyen_bay_routes.index'))
    
@chuyen_bay_routes.route('/danh_sach_chuyen_bay_admin')
def danh_sach_chuyen_bay_admin():
    try:
        # Truy vấn danh sách chuyến bay kèm thông tin sân bay
        chuyen_bay_list = ChuyenBay.query \
            .options(
                joinedload(ChuyenBay.san_bay_di_ref),  # Load thông tin sân bay đi
                joinedload(ChuyenBay.san_bay_den_ref)  # Load thông tin sân bay đến
            ).all()

        quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
        return render_template(
            'danh_sach_chuyen_bay_admin.html',
            chuyen_bay_list=chuyen_bay_list,
            quyen=quyen
        )
    except Exception as e:
        flash(f'Có lỗi xảy ra khi tải danh sách chuyến bay: {str(e)}')
        return redirect(url_for('chuyen_bay_routes.index'))
    
    
