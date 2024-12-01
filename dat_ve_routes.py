from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from db_utils import authenticate_user
from extensions import db
from datetime import datetime, timedelta
from vnpay import vnpay
from models import SanBay, ChuyenBay, LichChuyenBay, VeChuyenBay, QuyDinh, ThanhToan, DatVeChuyenBay

dat_ve_routes = Blueprint('dat_ve_routes', __name__)


@dat_ve_routes.route('/danh_sach_dat_ve', methods=['GET'])
def danh_sach_dat_ve():
    # Lấy danh sách sân bay ngay từ đầu, luôn có dữ liệu
    danh_sach_san_bay_di = db.session.query(SanBay).join(ChuyenBay, ChuyenBay.san_bay_di == SanBay.ma_san_bay).distinct().all()
    danh_sach_san_bay_den = db.session.query(SanBay).join(ChuyenBay, ChuyenBay.san_bay_den == SanBay.ma_san_bay).distinct().all()

    # Dữ liệu tìm kiếm (nếu có)
    san_bay_di_selected = request.args.get('san_bay_di', '')
    san_bay_den_selected = request.args.get('san_bay_den', '')
    ngay_khoi_hanh = request.args.get('ngay_khoi_hanh', '')

    # Tìm kiếm chuyến bay
    query = db.session.query(
        ChuyenBay.ma_chuyen_bay,
        ChuyenBay.san_bay_di,
        ChuyenBay.san_bay_den,
        LichChuyenBay.ngay_gio_khoi_hanh,
        VeChuyenBay.gia,
        VeChuyenBay.ma_ve,
        VeChuyenBay.hang_ve,
        LichChuyenBay.ma_lich_chuyen_bay
    ).join(LichChuyenBay, ChuyenBay.ma_chuyen_bay == LichChuyenBay.ma_chuyen_bay
    ).join(VeChuyenBay, ChuyenBay.ma_chuyen_bay == VeChuyenBay.ma_chuyen_bay)

    # Áp dụng bộ lọc nếu có
    if san_bay_di_selected:
        query = query.filter(ChuyenBay.san_bay_di == san_bay_di_selected)
    if san_bay_den_selected:
        query = query.filter(ChuyenBay.san_bay_den == san_bay_den_selected)
    if ngay_khoi_hanh:
        try:
            ngay_khoi_hanh_date = datetime.strptime(ngay_khoi_hanh, '%Y-%m-%d')
            query = query.filter(LichChuyenBay.ngay_gio_khoi_hanh >= ngay_khoi_hanh_date)
        except ValueError:
            pass

    # Điều kiện về thời gian đặt vé
    query = query.filter(
        db.func.timestampdiff(
            db.text('HOUR'), db.func.now(), LichChuyenBay.ngay_gio_khoi_hanh
        ) >= db.session.query(QuyDinh.so_gio_dat_ve_truoc).scalar()
    )
    chuyen_bay_list = query.all()

    quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
    return render_template(
        'danh_sach_dat_ve.html',
        danh_sach_san_bay_di=danh_sach_san_bay_di,
        danh_sach_san_bay_den=danh_sach_san_bay_den,
        san_bay_di_selected=san_bay_di_selected,
        san_bay_den_selected=san_bay_den_selected,
        ngay_khoi_hanh=ngay_khoi_hanh,
        chuyen_bay_list=chuyen_bay_list,
        quyen=quyen
    )


@dat_ve_routes.route('/vnpay_payment', methods=['POST'])
def vnpay_payment():
    if request.method == 'POST':
        # Lấy thông tin từ form
        ma_ve_post = request.form['ma_ve']
        ma_lich_chuyen_bay = request.form['ma_lich_chuyen_bay']
        ho_ten = request.form['ho_ten']
        cmnd_cccd = request.form['cmnd_cccd']
        so_dien_thoai = request.form['so_dien_thoai']
        pttt = request.form['pttt']
        order_type = request.form.get('order_type')
        amount = int(request.form.get('amount'))
        order_desc = request.form.get('order_desc')
        bank_code = request.form.get('bank_code')
        language = request.form.get('language')

        # Lấy thông tin vé, lịch chuyến bay và quy định
        ve_chuyen_bay = VeChuyenBay.query.filter_by(ma_ve=ma_ve_post).first()
        lich_chuyen_bay = LichChuyenBay.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay).first()
        quy_dinh = QuyDinh.query.first()

        print(f"ve_chuyen_bay: {ve_chuyen_bay}")
        print(f"lich_chuyen_bay: {lich_chuyen_bay}")
        print(f"quy_dinh: {quy_dinh}")

        if not ve_chuyen_bay or not lich_chuyen_bay or not quy_dinh:
            flash('Thông tin vé hoặc lịch chuyến bay không hợp lệ.', 'error')
            return redirect(url_for('dat_ve_routes.danh_sach_dat_ve'))

        # Kiểm tra thời gian đặt vé
        thoi_gian_dat_ve = lich_chuyen_bay.ngay_gio_khoi_hanh - timedelta(hours=quy_dinh.so_gio_dat_ve_truoc)
        if datetime.now() > thoi_gian_dat_ve:
            flash('Không thể đặt vé do đã quá thời gian cho phép.', 'error')
            return redirect(url_for('dat_ve_routes.danh_sach_dat_ve'))

        # Kiểm tra số ghế đã đặt
        booked_seats_hang_1 = DatVeChuyenBay.query.join(VeChuyenBay).filter(
            DatVeChuyenBay.ma_lich_chuyen_bay == ma_lich_chuyen_bay,
            VeChuyenBay.hang_ve == 'Hạng 1'
        ).count()

        booked_seats_hang_2 = DatVeChuyenBay.query.join(VeChuyenBay).filter(
            DatVeChuyenBay.ma_lich_chuyen_bay == ma_lich_chuyen_bay,
            VeChuyenBay.hang_ve == 'Hạng 2'
        ).count()

        if ve_chuyen_bay.hang_ve == 'Hạng 1' and booked_seats_hang_1 >= lich_chuyen_bay.so_ghe_hang_1:
            flash('Không thể đặt vé do hết chỗ ở hạng 1.', 'error')
            return redirect(url_for('dat_ve_routes.danh_sach_dat_ve'))

        if ve_chuyen_bay.hang_ve == 'Hạng 2' and booked_seats_hang_2 >= lich_chuyen_bay.so_ghe_hang_2:
            flash('Không thể đặt vé do hết chỗ ở hạng 2.', 'error')
            return redirect(url_for('dat_ve_routes.danh_sach_dat_ve'))

        # Tạo đơn đặt vé
        dat_ve = DatVeChuyenBay(
            ho_ten=ho_ten,
            cmnd_cccd=cmnd_cccd,
            so_dien_thoai=so_dien_thoai,
            ma_ve=ma_ve_post,
            ma_lich_chuyen_bay=ma_lich_chuyen_bay
        )
        db.session.add(dat_ve)
        db.session.commit()

        # Tạo thông tin thanh toán
        thanh_toan = ThanhToan(
            ma_dat_ve=dat_ve.ma_dat_ve,
            pttt=pttt,
            trang_thai='Thành công',
            so_tien=amount
        )
        db.session.add(thanh_toan)
        db.session.commit()

        # Cấu hình VNPay
        vnp = vnpay()
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = 'X66MTG0V'
        vnp.requestData['vnp_Amount'] = amount * 100
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = f"{dat_ve.ma_dat_ve}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        vnp.requestData['vnp_OrderInfo'] = order_desc
        vnp.requestData['vnp_OrderType'] = order_type
        vnp.requestData['vnp_Locale'] = language if language else 'vn'
        vnp.requestData['vnp_BankCode'] = bank_code if bank_code else ''
        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = request.remote_addr
        vnp.requestData['vnp_ReturnUrl'] = url_for('dat_ve_routes.vnpay_return', _external=True)

        # Tạo URL thanh toán
        vnpay_payment_url = vnp.get_payment_url('https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
                                                'CBOBJWUW1HBHQQESTURDT7AEMJJOFXIR')
        return redirect(vnpay_payment_url)

    flash('Invalid request', 'error')
    return redirect(url_for('dat_ve_routes.danh_sach_dat_ve'))


@dat_ve_routes.route('/vnpay_return', methods=['GET'])
def vnpay_return():
    vnp_TransactionNo = request.args.get('vnp_TransactionNo')
    vnp_TxnRef = request.args.get('vnp_TxnRef')
    vnp_Amount = request.args.get('vnp_Amount')
    vnp_ResponseCode = request.args.get('vnp_ResponseCode')

    if vnp_ResponseCode == '00':
        try:
            ma_ve = vnp_TxnRef.split("-")[0]
            dat_ve = DatVeChuyenBay.query.filter(DatVeChuyenBay.ma_ve == ma_ve).first()
            if dat_ve:
                thanh_toan = ThanhToan.query.filter(ThanhToan.ma_dat_ve == dat_ve.ma_dat_ve).first()
                if thanh_toan:
                    thanh_toan.trang_thai = 'Thành công'
                    db.session.commit()
                    flash('Cập nhật trạng thái thanh toán thành công.')
                else:
                    flash('Không tìm thấy thông tin thanh toán.')
            else:
                flash('Không tìm thấy thông tin đặt vé.')
        except Exception as e:
            print(f"Error updating database: {str(e)}")
            db.session.rollback()
            flash('Lỗi cập nhật trạng thái thanh toán.')

    else:
        flash('Lỗi thanh toán. Vui lòng thử lại hoặc liên hệ với hỗ trợ.')

    quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')
    return render_template('vnpay_return.html', transaction_no=vnp_TransactionNo, txn_ref=vnp_TxnRef,
                           amount=vnp_Amount, response_code=vnp_ResponseCode, quyen=quyen)



@dat_ve_routes.route('/dat_ve/<ma_ve>/<ma_lich_chuyen_bay>', methods=['GET', 'POST'])
def dat_ve(ma_ve, ma_lich_chuyen_bay):
    quyen = session.get('user', {}).get('vai_tro', 'Khách hàng')

    if request.method == 'GET':
        ve_chuyen_bay = VeChuyenBay.query.filter_by(ma_ve=ma_ve).first()
        lich_chuyen_bay = LichChuyenBay.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay).first()
        quy_dinh = QuyDinh.query.first()

        if ve_chuyen_bay and lich_chuyen_bay and quy_dinh:
            thoi_gian_dat_ve = lich_chuyen_bay.ngay_gio_khoi_hanh - timedelta(hours=quy_dinh.so_gio_dat_ve_truoc)

            if datetime.now() < thoi_gian_dat_ve:
                # Tính số ghế đã đặt
                so_ghe_hang_1 = lich_chuyen_bay.so_ghe_hang_1
                so_ghe_hang_2 = lich_chuyen_bay.so_ghe_hang_2

                booked_seats_hang_1 = db.session.query(db.func.count(DatVeChuyenBay.ma_dat_ve))\
                    .join(VeChuyenBay, DatVeChuyenBay.ma_ve == VeChuyenBay.ma_ve)\
                    .filter(DatVeChuyenBay.ma_lich_chuyen_bay == ma_lich_chuyen_bay, VeChuyenBay.hang_ve == 'Hạng 1')\
                    .scalar()

                booked_seats_hang_2 = db.session.query(db.func.count(DatVeChuyenBay.ma_dat_ve))\
                    .join(VeChuyenBay, DatVeChuyenBay.ma_ve == VeChuyenBay.ma_ve)\
                    .filter(DatVeChuyenBay.ma_lich_chuyen_bay == ma_lich_chuyen_bay, VeChuyenBay.hang_ve == 'Hạng 2')\
                    .scalar()

                # Kiểm tra số ghế còn trống
                if ve_chuyen_bay.hang_ve == 'Hạng 1' and booked_seats_hang_1 < so_ghe_hang_1 or \
                   ve_chuyen_bay.hang_ve == 'Hạng 2' and booked_seats_hang_2 < so_ghe_hang_2:
                    return render_template('dat_ve.html', ve_chuyen_bay=ve_chuyen_bay,
                                           ma_lich_chuyen_bay=ma_lich_chuyen_bay, quyen=quyen)
                else:
                    flash('Không thể đặt vé cho chuyến bay này do hết chỗ.')
                    return redirect(url_for('dat_ve_routes.danh_sach_dat_ve'))

            else:
                flash('Không thể đặt vé cho chuyến bay này do đã quá thời gian đặt vé.')
                return redirect(url_for('dat_ve_routes.danh_sach_dat_ve'))

        flash('Không tìm thấy thông tin chuyến bay.')
        return redirect(url_for('dat_ve_routes.danh_sach_dat_ve'))
    
@dat_ve_routes.route('/khuyen_mai')
def khuyen_mai():
    return render_template('khuyen_mai.html')
