from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from db_utils import authenticate_user
from models import SanBay, ChuyenBay
from extensions import db


authentication_routes = Blueprint('authentication_routes', __name__)


@authentication_routes.route('/')
def index():
    # Xóa thông tin người dùng trong session khi người dùng quay lại trang login
    session.pop('user', None)

    # Tạo session cho người dùng mới (chưa đăng nhập)
    session['user'] = {
        'ma_nguoi_dung': "No", 
        'ten_nguoi_dung': "No", 
        'email': "No", 
        'phone': "No", 
        'mat_khau': "No", 
        'vai_tro': "Khách hàng"
    }
    return render_template('login.html')

@authentication_routes.route('/dang_nhap', methods=['POST'])
def dang_nhap():
    email = request.form.get('email')
    password = request.form.get('mat_khau')

    # Kiểm tra xác thực người dùng
    user = authenticate_user(email, password)
    
    if user:
        # Lưu thông tin người dùng vào session
        session['user'] = {
            'ma_nguoi_dung': user.ma_nguoi_dung, 
            'ten_nguoi_dung': user.ten_nguoi_dung,
            'email': user.email, 
            'phone': user.phone, 
            'vai_tro': user.vai_tro
        }

        # Dựa trên vai trò của người dùng, điều hướng tới trang tương ứng
        if user.vai_tro == 'Người quản trị':
            return redirect(url_for('.trang_admin'))
        elif user.vai_tro == 'Nhân viên':
            return redirect(url_for('.trang_nhan_vien'))
        elif user.vai_tro == 'Khách hàng':
            return redirect(url_for('.trang_khach_hang'))
    else:
        flash('Email hoặc mật khẩu không đúng!', 'error')
        return redirect(url_for('.index'))
    
@authentication_routes.route('/trang_admin')
def trang_admin():
    # Kiểm tra quyền truy cập của người dùng
    if 'user' in session and session['user']['vai_tro'] == 'Người quản trị':
        quyen = session['user']['vai_tro']
        return render_template('trang_admin.html', quyen=quyen)
    else:
        flash('Truy cập bị từ chối. Vui lòng đăng nhập với tư cách Admin.', 'error')
        return redirect(url_for('.dang_nhap'))
    
@authentication_routes.route('/trang_nhan_vien')
def trang_nhan_vien():
    # Kiểm tra quyền truy cập của người dùng
    if 'user' in session and session['user']['vai_tro'] == 'Nhân viên':
        quyen = session['user']['vai_tro']
        return render_template('trang_nhan_vien.html', quyen=quyen)
    else:
        flash('Truy cập bị từ chối. Vui lòng đăng nhập với tư cách Nhân viên.', 'error')
        return redirect(url_for('.dang_nhap'))

@authentication_routes.route('/trang_khach_hang')
def trang_khach_hang():
    # Lấy quyền của người dùng từ session
    quyen = session['user']['vai_tro']

    # Lấy danh sách sân bay để hiển thị form tìm kiếm
    danh_sach_san_bay_di = db.session.query(SanBay).join(ChuyenBay, ChuyenBay.san_bay_di == SanBay.ma_san_bay).distinct().all()
    danh_sach_san_bay_den = db.session.query(SanBay).join(ChuyenBay, ChuyenBay.san_bay_den == SanBay.ma_san_bay).distinct().all()

    return render_template(
        'danh_sach_dat_ve.html',
        quyen=quyen,
        danh_sach_san_bay_di=danh_sach_san_bay_di,
        danh_sach_san_bay_den=danh_sach_san_bay_den,
        san_bay_di_selected='',  # Không có giá trị mặc định
        san_bay_den_selected='',
        ngay_khoi_hanh=''
    )





