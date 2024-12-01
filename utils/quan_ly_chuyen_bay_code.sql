CREATE TABLE quy_dinh (
    ma_quy_dinh INT AUTO_INCREMENT PRIMARY KEY,
    so_luong_san_bay INT,
    thoi_gian_bay_toi_thieu INT,
    so_san_bay_trung_gian_toi_da INT,
    thoi_gian_dung_toi_thieu INT,
    thoi_gian_dung_toi_da INT,
    so_gio_dat_ve_truoc INT,
    so_gio_ban_ve_truoc INT
);
INSERT INTO quy_dinh 
(so_luong_san_bay, thoi_gian_bay_toi_thieu, so_san_bay_trung_gian_toi_da, 
thoi_gian_dung_toi_thieu, thoi_gian_dung_toi_da, so_gio_dat_ve_truoc, so_gio_ban_ve_truoc)
VALUES
(10, 30, 2, 20, 30, 12, 4);

CREATE TABLE nguoi_dung (
    ma_nguoi_dung VARCHAR(10) PRIMARY KEY,
    ten_nguoi_dung VARCHAR(50) NOT NULL,
    mat_khau VARCHAR(200) NOT NULL,
    vai_tro VARCHAR(10) CHECK (vai_tro IN (N'Admin', N'Nhân viên'))
);
INSERT INTO nguoi_dung (ma_nguoi_dung, ten_nguoi_dung, mat_khau, vai_tro)
VALUES
('admin', N'Người quản trị', MD5('123'), N'Admin'),
('nhanvien', N'Nhân viên', MD5('123'), N'Nhân viên');


CREATE TABLE san_bay (
    ma_san_bay VARCHAR(10) PRIMARY KEY,
    ten_san_bay VARCHAR(100) NOT NULL,
    tinh_thanh VARCHAR(30) NOT NULL,
    quoc_gia VARCHAR(30) NOT NULL
);
INSERT INTO san_bay 
(ma_san_bay, ten_san_bay, tinh_thanh, quoc_gia)
VALUES
('SGN', N'Sân bay Tân Sơn Nhất', N'TP.Hồ Chí Minh', N'Việt Nam'),
('HAN', N'Sân bay Nội Bài', N'Hà Nội', N'Việt Nam'),
('DAD', N'Sân bay Đà Nẵng', N'Đà Nẵng', N'Việt Nam'),
('VCA', N'Sân bay Cần Thơ', N'Cần Thơ', N'Việt Nam'),
('PQC', N'Sân bay Phú Quốc', N'Kiên Giang', N'Việt Nam'),
('VDO', N'Sân bay Vân Đồn', N'Quảng Ninh', N'Việt Nam'),
('CXR', N'Sân bay Cam Ranh', N'Khánh Hòa', N'Việt Nam'),
('VII', N'Sân bay Vinh', N'TP.Hồ Chí Minh', N'Việt Nam'),
('HUI', N'Sân bay Phú Bài', N'Thừa Thiên Huế', N'Việt Nam'),
('UIH', N'Sân bay Phù Cát', N'Bình Định', N'Việt Nam');

CREATE TABLE chuyen_bay (
    ma_chuyen_bay VARCHAR(10) PRIMARY KEY,
    san_bay_di VARCHAR(10),
    san_bay_den VARCHAR(10),
    FOREIGN KEY (san_bay_di) REFERENCES san_bay(ma_san_bay),
    FOREIGN KEY (san_bay_den) REFERENCES san_bay(ma_san_bay)
);
INSERT INTO chuyen_bay 
(ma_chuyen_bay, san_bay_di, san_bay_den)
VALUES
('VN1200', 'SGN', 'HAN'),
('VN1201', 'HAN', 'DAD'),
('VN1202', 'DAD', 'PQC'),
('VN1203', 'SGN', 'VCA'),
('VN1204', 'HAN', 'PQC');
CREATE TABLE ve_chuyen_bay (
    ma_ve INT AUTO_INCREMENT PRIMARY KEY,
    ma_chuyen_bay VARCHAR(10),
    hang_ve VARCHAR(20) NOT NULL,
    gia INT NOT NULL,
    FOREIGN KEY (ma_chuyen_bay) REFERENCES chuyen_bay(ma_chuyen_bay) ON DELETE CASCADE
);

INSERT INTO ve_chuyen_bay (ma_chuyen_bay, hang_ve, gia)
VALUES
('VN1200', N'Hạng 1', 1500000),
('VN1200', N'Hạng 2', 800000),
('VN1201', N'Hạng 1', 1200000),
('VN1201', N'Hạng 2', 650000),
('VN1202', N'Hạng 1', 1300000),
('VN1202', N'Hạng 2', 700000),
('VN1203', N'Hạng 1', 1400000),
('VN1203', N'Hạng 2', 750000),
('VN1204', N'Hạng 1', 1600000),
('VN1204', N'Hạng 2', 850000);
CREATE TABLE lich_chuyen_bay (
    ma_lich_chuyen_bay INT AUTO_INCREMENT PRIMARY KEY,
    ngay_gio_khoi_hanh DATETIME NOT NULL,
    ma_chuyen_bay VARCHAR(10),
    thoi_gian_bay_phut INT NOT NULL,
    so_ghe_hang_1 INT NOT NULL,
    so_ghe_hang_2 INT NOT NULL,
    FOREIGN KEY (ma_chuyen_bay) REFERENCES chuyen_bay(ma_chuyen_bay) ON DELETE CASCADE
);

INSERT INTO lich_chuyen_bay 
(ma_chuyen_bay, ngay_gio_khoi_hanh, thoi_gian_bay_phut, so_ghe_hang_1, so_ghe_hang_2)
VALUES
('VN1200', '2024-01-10 08:00:00', 120, 50, 100),
('VN1201', '2024-01-11 10:30:00', 90, 30, 80),
('VN1202', '2024-01-12 15:45:00', 60, 20, 50),
('VN1203', '2024-01-13 12:15:00', 75, 40, 60),
('VN1204', '2024-01-14 09:20:00', 120, 60, 90);

CREATE TABLE san_bay_trung_gian (
    stt INT NOT NULL,
    ma_lich_chuyen_bay INT NOT NULL,
    san_bay_trung_gian VARCHAR(10) NOT NULL,
    thoi_gian_dung_phut INT,
    ghi_chu VARCHAR(200),
    PRIMARY KEY(stt, ma_lich_chuyen_bay, san_bay_trung_gian),
    FOREIGN KEY (ma_lich_chuyen_bay) REFERENCES lich_chuyen_bay(ma_lich_chuyen_bay) ON DELETE CASCADE,
    FOREIGN KEY (san_bay_trung_gian) REFERENCES san_bay(ma_san_bay)
);
INSERT INTO san_bay_trung_gian 
(stt, ma_lich_chuyen_bay, san_bay_trung_gian, thoi_gian_dung_phut, ghi_chu)
VALUES
(1, 1, 'DAD', 30, N'Dừng chân tại Đà Nẵng'),
(2, 2, 'CXR', 20, N'Dừng chân tại Cam Ranh'),
(3, 3, 'VDO', 25, N'Dừng chân tại Vân Đồn'),
(1, 4, 'VCA', 30, N'Dừng chân tại Cần Thơ'),
(2, 5, 'VCA', 30, N'Dừng chân tại Cần Thơ');


CREATE TABLE dat_ve_chuyen_bay (
    ma_dat_ve INT AUTO_INCREMENT PRIMARY KEY,
    ho_ten VARCHAR(100) NOT NULL,
    cmnd_cccd VARCHAR(20) NOT NULL,
    so_dien_thoai VARCHAR(15) NOT NULL,
    ma_ve INT,
    ma_lich_chuyen_bay INT,
    thoi_diem_dat_ve DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ma_ve) REFERENCES ve_chuyen_bay(ma_ve) ON DELETE CASCADE,
    FOREIGN KEY (ma_lich_chuyen_bay) REFERENCES lich_chuyen_bay(ma_lich_chuyen_bay)  ON DELETE CASCADE
);
INSERT INTO dat_ve_chuyen_bay (ho_ten, cmnd_cccd, so_dien_thoai, ma_ve, ma_lich_chuyen_bay)
VALUES
('Nguyễn Văn A', '123456789', '0901234567', 1, 1),
('Trần Thị B', '987654321', '0987654321', 2, 1),
('Lê Văn C', '567890123', '0123456789', 3, 1),
('Phạm Thị D', '321098765', '0123456789', 4, 2),
('Ngô Văn E', '456789012', '0987654321', 5, 2),
('Đinh Thị F', '789012345', '0901234567', 6, 3),
('Trương Văn G', '234567890', '0987654321', 7, 1),
('Lê Thị H', '890123456', '0123456789', 8, 3),
('Nguyễn Văn I', '012345678', '0901234567', 9, 5),
('Phạm Thị K', '345678901', '0987654321', 10, 1),
('Hoàng Văn L', '567890234', '0901234567', 1, 4),
('Lê Thị M', '789012345', '0123456789', 2, 3),
('Nguyễn Văn N', '123456789', '0987654321', 3, 5),
('Trần Thị P', '234567890', '0901234567', 4, 1),
('Phạm Văn Q', '345678901', '0123456789', 5, 5),
('Đinh Thị R', '456789012', '0987654321', 6, 3),
('Nguyễn Thị S', '567890123', '0901234567', 7, 4),
('Lê Văn T', '678901234', '0123456789', 8, 4),
('Trần Văn U', '789012345', '0987654321', 9, 4),
('Phạm Thị V', '890123456', '0901234567', 10, 1);


CREATE TABLE thanh_toan (
    ma_thanh_toan INT AUTO_INCREMENT PRIMARY KEY,
    ngay_thanh_toan DATETIME DEFAULT CURRENT_TIMESTAMP,
    pttt VARCHAR(50) NOT NULL,
    trang_thai VARCHAR(50),
    so_tien BIGINT DEFAULT 0,
    ma_dat_ve INT,
    FOREIGN KEY (ma_dat_ve) REFERENCES dat_ve_chuyen_bay(ma_dat_ve) ON DELETE CASCADE
);

INSERT INTO thanh_toan (pttt, trang_thai, ma_dat_ve, so_tien)
VALUES
('Ví điện tử', 'Thành công', 1, 1500000),
('Thẻ tín dụng', 'Đang xử lý', 2, 800000),
('Chuyển khoản', 'Thành công', 3, 1200000),
('Tiền mặt', 'Đang xử lý', 4, 650000),
('Ví điện tử', 'Thành công', 5, 1300000),
('Thẻ tín dụng', 'Đang xử lý', 6, 700000),
('Chuyển khoản', 'Thành công', 7, 1400000),
('Tiền mặt', 'Đang xử lý', 8, 750000),
('Ví điện tử', 'Thành công', 9, 1600000),
('Thẻ tín dụng', 'Đang xử lý', 10, 850000),
('Ví điện tử', 'Thành công', 11, 1500000),
('Thẻ tín dụng', 'Đang xử lý', 12, 800000),
('Chuyển khoản', 'Thành công', 13, 1200000),
('Tiền mặt', 'Đang xử lý', 14, 650000),
('Ví điện tử', 'Thành công', 15, 1300000),
('Thẻ tín dụng', 'Đang xử lý', 16, 700000),
('Chuyển khoản', 'Thành công', 17, 1400000),
('Tiền mặt', 'Đang xử lý', 18, 750000),
('Ví điện tử', 'Thành công', 19, 1600000),
('Thẻ tín dụng', 'Đang xử lý', 20, 850000);
