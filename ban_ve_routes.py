from flask import Blueprint, render_template, redirect, url_for, flash, session, request
# from db_utils import cursor, db
from datetime import datetime, timedelta
from extensions import db
from models import SanBay, ChuyenBay, LichChuyenBay, VeChuyenBay, QuyDinh, DatVeChuyenBay, ThanhToan

ban_ve_routes = Blueprint('ban_ve_routes', __name__)


@ban_ve_routes.route('/danh_sach_ban_ve')
def danh_sach_ban_ve():
    # Lấy danh sách sân bay đi
    danh_sach_san_bay_di = db.session.query(SanBay.ma_san_bay, SanBay.ten_san_bay)\
        .join(ChuyenBay, ChuyenBay.san_bay_di == SanBay.ma_san_bay)\
        .distinct().all()

    # Lấy danh sách sân bay đến
    danh_sach_san_bay_den = db.session.query(SanBay.ma_san_bay, SanBay.ten_san_bay)\
        .join(ChuyenBay, ChuyenBay.san_bay_den == SanBay.ma_san_bay)\
        .distinct().all()

    # Lấy thông tin từ form nếu có
    san_bay_di_selected = request.args.get('san_bay_di', '')
    san_bay_den_selected = request.args.get('san_bay_den', '')
    ngay_khoi_hanh = request.args.get('ngay_khoi_hanh', '')

    # Query chuyến bay
    query = db.session.query(
        ChuyenBay.ma_chuyen_bay,
        ChuyenBay.san_bay_di,
        ChuyenBay.san_bay_den,
        LichChuyenBay.ngay_gio_khoi_hanh,
        VeChuyenBay.gia,
        VeChuyenBay.ma_ve,
        VeChuyenBay.hang_ve,
        LichChuyenBay.ma_lich_chuyen_bay
    ).join(LichChuyenBay, LichChuyenBay.ma_chuyen_bay == ChuyenBay.ma_chuyen_bay)\
     .join(VeChuyenBay, VeChuyenBay.ma_chuyen_bay == ChuyenBay.ma_chuyen_bay)

    if san_bay_di_selected:
        query = query.filter(ChuyenBay.san_bay_di == san_bay_di_selected)

    if san_bay_den_selected:
        query = query.filter(ChuyenBay.san_bay_den == san_bay_den_selected)

    if ngay_khoi_hanh:
        query = query.filter(db.func.date(LichChuyenBay.ngay_gio_khoi_hanh) == ngay_khoi_hanh)

    # Lấy điều kiện so_gio_dat_ve_truoc từ bảng QuyDinh
    quy_dinh = QuyDinh.query.first()
    if quy_dinh:
        query = query.filter(
            db.func.timestampdiff(db.text('HOUR'), datetime.now(), LichChuyenBay.ngay_gio_khoi_hanh) >= quy_dinh.so_gio_dat_ve_truoc
        )

    chuyen_bay_list = query.all()

    # Lấy quyền từ session
    quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')

    return render_template(
        'danh_sach_ban_ve.html',
        danh_sach_san_bay_di=danh_sach_san_bay_di,
        danh_sach_san_bay_den=danh_sach_san_bay_den,
        san_bay_di_selected=san_bay_di_selected,
        san_bay_den_selected=san_bay_den_selected,
        ngay_khoi_hanh=ngay_khoi_hanh,
        chuyen_bay_list=chuyen_bay_list,
        quyen=quyen
    )
    
@ban_ve_routes.route('/ban_ve/<ma_ve>/<ma_lich_chuyen_bay>', methods=['GET', 'POST'])
def ban_ve(ma_ve, ma_lich_chuyen_bay):
    quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')

    if request.method == 'GET':
        # Lấy thông tin vé và các liên kết khác
        ve_chuyen_bay = db.session.query(VeChuyenBay)\
            .join(ChuyenBay, VeChuyenBay.ma_chuyen_bay == ChuyenBay.ma_chuyen_bay)\
            .join(LichChuyenBay, ChuyenBay.ma_chuyen_bay == LichChuyenBay.ma_chuyen_bay)\
            .filter(VeChuyenBay.ma_ve == ma_ve).first()

        lich_chuyen_bay = LichChuyenBay.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay).first()

        quy_dinh = db.session.query(QuyDinh).first()

        if not ve_chuyen_bay or not quy_dinh:
            flash('Không tìm thấy thông tin chuyến bay hoặc quy định.')
            return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))

        # Kiểm tra thời gian đặt vé
        thoi_gian_ban_ve_truoc = lich_chuyen_bay.ngay_gio_khoi_hanh - timedelta(hours=quy_dinh.so_gio_dat_ve_truoc)
        if datetime.now() >= thoi_gian_ban_ve_truoc:
            flash('Không thể đặt vé cho chuyến bay này do đã quá thời gian đặt vé.')
            return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))

        # Tính số ghế đã đặt
        booked_seats_hang_1 = db.session.query(DatVeChuyenBay)\
            .join(VeChuyenBay, DatVeChuyenBay.ma_ve == VeChuyenBay.ma_ve)\
            .filter(DatVeChuyenBay.ma_lich_chuyen_bay == ma_lich_chuyen_bay, VeChuyenBay.hang_ve == 'Hạng 1').count()

        booked_seats_hang_2 = db.session.query(DatVeChuyenBay)\
            .join(VeChuyenBay, DatVeChuyenBay.ma_ve == VeChuyenBay.ma_ve)\
            .filter(DatVeChuyenBay.ma_lich_chuyen_bay == ma_lich_chuyen_bay, VeChuyenBay.hang_ve == 'Hạng 2').count()

        # Kiểm tra ghế còn trống
        so_ghe_hang_1 = lich_chuyen_bay.so_ghe_hang_1
        so_ghe_hang_2 = lich_chuyen_bay.so_ghe_hang_2

        if booked_seats_hang_1 < so_ghe_hang_1 or booked_seats_hang_2 < so_ghe_hang_2:
            return render_template('ban_ve.html', ve_chuyen_bay=ve_chuyen_bay, ma_lich_chuyen_bay=ma_lich_chuyen_bay, quyen=quyen)

        flash('Không thể đặt vé cho chuyến bay này do hết chỗ.')
        return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))

    elif request.method == 'POST':
        # Lấy thông tin từ form
        ho_ten = request.form['ho_ten']
        cmnd_cccd = request.form['cmnd_cccd']
        so_dien_thoai = request.form['so_dien_thoai']
        so_tien = request.form['so_tien']

        # Kiểm tra thông tin vé
        ve_chuyen_bay = db.session.query(VeChuyenBay)\
            .join(ChuyenBay, VeChuyenBay.ma_chuyen_bay == ChuyenBay.ma_chuyen_bay)\
            .join(LichChuyenBay, ChuyenBay.ma_chuyen_bay == LichChuyenBay.ma_chuyen_bay)\
            .filter(VeChuyenBay.ma_ve == ma_ve).first()
            
        lich_chuyen_bay = LichChuyenBay.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay).first()

        quy_dinh = db.session.query(QuyDinh).first()

        if not ve_chuyen_bay or not quy_dinh:
            flash('Không tìm thấy thông tin chuyến bay hoặc quy định.')
            return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))


        # Kiểm tra thời gian bán vé
        thoi_gian_ban_ve_truoc = lich_chuyen_bay.ngay_gio_khoi_hanh - timedelta(hours=quy_dinh.so_gio_dat_ve_truoc)
        if datetime.now() >= thoi_gian_ban_ve_truoc:
            flash('Không thể đặt vé cho chuyến bay này do đã quá thời gian bán vé.')
            return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))

        # Kiểm tra số ghế đã đặt cho từng hạng
        booked_seats_hang_1 = db.session.query(DatVeChuyenBay)\
            .join(VeChuyenBay, DatVeChuyenBay.ma_ve == VeChuyenBay.ma_ve)\
            .filter(DatVeChuyenBay.ma_lich_chuyen_bay == ma_lich_chuyen_bay, VeChuyenBay.hang_ve == 'Hạng 1').count()

        booked_seats_hang_2 = db.session.query(DatVeChuyenBay)\
            .join(VeChuyenBay, DatVeChuyenBay.ma_ve == VeChuyenBay.ma_ve)\
            .filter(DatVeChuyenBay.ma_lich_chuyen_bay == ma_lich_chuyen_bay, VeChuyenBay.hang_ve == 'Hạng 2').count()

        # Lấy tổng số ghế của từng hạng từ thông tin chuyến bay
        so_ghe_hang_1 = lich_chuyen_bay.so_ghe_hang_1
        so_ghe_hang_2 = lich_chuyen_bay.so_ghe_hang_2

        # Kiểm tra ghế trống
        if booked_seats_hang_1 >= so_ghe_hang_1 and booked_seats_hang_2 >= so_ghe_hang_2:
            flash('Không thể đặt vé cho chuyến bay này do hết chỗ.')
            return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))
        
        # Tạo thông tin đặt vé
        dat_ve = DatVeChuyenBay(
            ho_ten=ho_ten,
            cmnd_cccd=cmnd_cccd,
            so_dien_thoai=so_dien_thoai,
            ma_ve=ma_ve,
            ma_lich_chuyen_bay=ma_lich_chuyen_bay
        )
        db.session.add(dat_ve)
        db.session.commit()

        # Lấy mã đặt vé vừa được thêm
        ma_dat_ve = dat_ve.ma_dat_ve

        # Thêm thông tin thanh toán
        thanh_toan = ThanhToan(
            ma_dat_ve=ma_dat_ve,
            pttt='Tại quầy',
            trang_thai='Thành công',
            so_tien=so_tien
        )
        db.session.add(thanh_toan)
        db.session.commit()

        flash('Bán vé và thanh toán thành công.')
        return redirect(url_for('ban_ve_routes.thong_tin_ve', ma_dat_ve=ma_dat_ve))


@ban_ve_routes.route('/thong_tin_ve/<ma_dat_ve>', methods=['GET'])
def thong_tin_ve(ma_dat_ve):
    try:
        # Truy vấn thông tin đặt vé
        result = db.session.query(
            DatVeChuyenBay,
            VeChuyenBay,
            ChuyenBay,
            LichChuyenBay
        ).join(
            VeChuyenBay, DatVeChuyenBay.ma_ve == VeChuyenBay.ma_ve
        ).join(
            ChuyenBay, VeChuyenBay.ma_chuyen_bay == ChuyenBay.ma_chuyen_bay
        ).join(
            LichChuyenBay, ChuyenBay.ma_chuyen_bay == LichChuyenBay.ma_chuyen_bay
        ).filter(
            DatVeChuyenBay.ma_dat_ve == ma_dat_ve
        ).first()

        if result:
            # Phân tách dữ liệu theo cấu trúc mong muốn
            dat_ve, ve_chuyen_bay, chuyen_bay, lich_chuyen_bay = result

            thong_tin_dat_ve = {
                "ho_ten": dat_ve.ho_ten,
                "cmnd_cccd": dat_ve.cmnd_cccd,
                "so_dien_thoai": dat_ve.so_dien_thoai,
                "ma_ve": dat_ve.ma_ve,
                "ma_lich_chuyen_bay": dat_ve.ma_lich_chuyen_bay,
                "thoi_diem_dat_ve": dat_ve.thoi_diem_dat_ve
            }

            thong_tin_ve_chuyen_bay = {
                "hang_ve": ve_chuyen_bay.hang_ve,
                "gia": ve_chuyen_bay.gia,
                "ma_chuyen_bay": ve_chuyen_bay.ma_chuyen_bay
            }

            thong_tin_chuyen_bay = {
                "san_bay_di": chuyen_bay.san_bay_di,
                "san_bay_den": chuyen_bay.san_bay_den,
                "ngay_gio_khoi_hanh": lich_chuyen_bay.ngay_gio_khoi_hanh,
                "thoi_gian_bay_phut": lich_chuyen_bay.thoi_gian_bay_phut
            }

            quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')

            return render_template(
                'thong_tin_ve.html',
                thong_tin_dat_ve=thong_tin_dat_ve,
                thong_tin_ve_chuyen_bay=thong_tin_ve_chuyen_bay,
                thong_tin_chuyen_bay=thong_tin_chuyen_bay,
                quyen=quyen
            )
        else:
            flash('Không tìm thấy thông tin đặt vé.')
            return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))
    except Exception as e:
        flash(f'Đã xảy ra lỗi: {str(e)}')
        return redirect(url_for('ban_ve_routes.danh_sach_ban_ve'))
