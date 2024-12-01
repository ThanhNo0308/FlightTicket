from extensions import db

class QuyDinh(db.Model):
    __tablename__ = 'quy_dinh'
    ma_quy_dinh = db.Column(db.Integer, primary_key=True, autoincrement=True)
    so_luong_san_bay = db.Column(db.Integer)
    thoi_gian_bay_toi_thieu = db.Column(db.Integer)
    so_san_bay_trung_gian_toi_da = db.Column(db.Integer)
    thoi_gian_dung_toi_thieu = db.Column(db.Integer)
    thoi_gian_dung_toi_da = db.Column(db.Integer)
    so_gio_dat_ve_truoc = db.Column(db.Integer)
    so_gio_ban_ve_truoc = db.Column(db.Integer)


class NguoiDung(db.Model):
    __tablename__ = 'nguoi_dung'
    ma_nguoi_dung = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_nguoi_dung = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    mat_khau = db.Column(db.String(200), nullable=False)
    vai_tro = db.Column(db.String(30), nullable=False)


class SanBay(db.Model):
    __tablename__ = 'san_bay'
    ma_san_bay = db.Column(db.String(10), primary_key=True)
    ten_san_bay = db.Column(db.String(100), nullable=False)
    tinh_thanh = db.Column(db.String(30), nullable=False)
    quoc_gia = db.Column(db.String(30), nullable=False)

    chuyen_bay_di = db.relationship('ChuyenBay', backref='san_bay_di_ref', foreign_keys='ChuyenBay.san_bay_di')
    chuyen_bay_den = db.relationship('ChuyenBay', backref='san_bay_den_ref', foreign_keys='ChuyenBay.san_bay_den')


class ChuyenBay(db.Model):
    __tablename__ = 'chuyen_bay'
    ma_chuyen_bay = db.Column(db.String(10), primary_key=True)
    san_bay_di = db.Column(db.String(10), db.ForeignKey('san_bay.ma_san_bay'))
    san_bay_den = db.Column(db.String(10), db.ForeignKey('san_bay.ma_san_bay'))

    lich_chuyen_bay = db.relationship('LichChuyenBay', back_populates='chuyen_bay')
    ve_chuyen_bay = db.relationship('VeChuyenBay', back_populates='chuyen_bay')


class VeChuyenBay(db.Model):
    __tablename__ = 've_chuyen_bay'
    ma_ve = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ma_chuyen_bay = db.Column(db.String(10), db.ForeignKey('chuyen_bay.ma_chuyen_bay', ondelete="CASCADE"))
    hang_ve = db.Column(db.String(20), nullable=False)
    gia = db.Column(db.Integer, nullable=False)

    chuyen_bay = db.relationship('ChuyenBay', back_populates='ve_chuyen_bay')
    dat_ve = db.relationship('DatVeChuyenBay', back_populates='ve_chuyen_bay')


class LichChuyenBay(db.Model):
    __tablename__ = 'lich_chuyen_bay'
    ma_lich_chuyen_bay = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ngay_gio_khoi_hanh = db.Column(db.DateTime, nullable=False)
    ma_chuyen_bay = db.Column(db.String(10), db.ForeignKey('chuyen_bay.ma_chuyen_bay', ondelete="CASCADE"))
    thoi_gian_bay_phut = db.Column(db.Integer, nullable=False)
    so_ghe_hang_1 = db.Column(db.Integer, nullable=False)
    so_ghe_hang_2 = db.Column(db.Integer, nullable=False)

    chuyen_bay = db.relationship('ChuyenBay', back_populates='lich_chuyen_bay')
    dat_ve_chuyen_bay = db.relationship('DatVeChuyenBay', back_populates='lich_chuyen_bay')
    san_bay_trung_gian = db.relationship('SanBayTrungGian', back_populates='lich_chuyen_bay')


class SanBayTrungGian(db.Model):
    __tablename__ = 'san_bay_trung_gian'
    stt = db.Column(db.Integer, nullable=False, primary_key=True)
    ma_lich_chuyen_bay = db.Column(db.Integer, db.ForeignKey('lich_chuyen_bay.ma_lich_chuyen_bay', ondelete="CASCADE"), primary_key=True)
    san_bay_trung_gian = db.Column(db.String(10), db.ForeignKey('san_bay.ma_san_bay'), primary_key=True)
    thoi_gian_dung_phut = db.Column(db.Integer)
    ghi_chu = db.Column(db.String(200))

    lich_chuyen_bay = db.relationship('LichChuyenBay', back_populates='san_bay_trung_gian')
    san_bay = db.relationship('SanBay')


class DatVeChuyenBay(db.Model):
    __tablename__ = 'dat_ve_chuyen_bay'
    ma_dat_ve = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ho_ten = db.Column(db.String(100), nullable=False)
    cmnd_cccd = db.Column(db.String(20), nullable=False)
    so_dien_thoai = db.Column(db.String(15), nullable=False)
    ma_ve = db.Column(db.Integer, db.ForeignKey('ve_chuyen_bay.ma_ve', ondelete="CASCADE"))
    ma_lich_chuyen_bay = db.Column(db.Integer, db.ForeignKey('lich_chuyen_bay.ma_lich_chuyen_bay', ondelete="CASCADE"))
    thoi_diem_dat_ve = db.Column(db.DateTime, default=db.func.current_timestamp())

    ve_chuyen_bay = db.relationship('VeChuyenBay', back_populates='dat_ve')
    lich_chuyen_bay = db.relationship('LichChuyenBay', back_populates='dat_ve_chuyen_bay')
    thanh_toan = db.relationship('ThanhToan', back_populates='dat_ve')


class ThanhToan(db.Model):
    __tablename__ = 'thanh_toan'
    ma_thanh_toan = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ngay_thanh_toan = db.Column(db.DateTime, default=db.func.current_timestamp())
    pttt = db.Column(db.String(50), nullable=False)
    trang_thai = db.Column(db.String(50))
    so_tien = db.Column(db.BigInteger, default=0)
    ma_dat_ve = db.Column(db.Integer, db.ForeignKey('dat_ve_chuyen_bay.ma_dat_ve', ondelete="CASCADE"))

    dat_ve = db.relationship('DatVeChuyenBay', back_populates='thanh_toan')
