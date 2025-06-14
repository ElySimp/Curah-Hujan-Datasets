-- Membuat database (jika belum ada)
CREATE DATABASE IF NOT EXISTS faldodwbmkg;
USE faldodwbmkg;

-- Tabel Dimensi Waktu
CREATE TABLE DimWaktu (
    waktu_id INT AUTO_INCREMENT PRIMARY KEY,
    tanggal DATE NOT NULL,
    bulan INT NOT NULL,
    tahun INT NOT NULL,
    nama_bulan VARCHAR(20) NOT NULL,
    UNIQUE KEY (tanggal)
);

-- Tabel Dimensi Lokasi
CREATE TABLE DimLokasi (
    lokasi_id INT AUTO_INCREMENT PRIMARY KEY,
    nama_lokasi VARCHAR(100) NOT NULL,
    jenis_lokasi ENUM('Kabupaten', 'Kota') NOT NULL,
    provinsi VARCHAR(100) DEFAULT 'Jawa Barat',
    nama_stasiun VARCHAR(100),
    id_wmo VARCHAR(20),
    lintang BIGINT,
    bujur BIGINT,
    elevasi DECIMAL(10, 2),
    UNIQUE KEY (nama_lokasi, jenis_lokasi)
);

-- Tabel Fakta Curah Hujan
CREATE TABLE FactDataIklim (
    fact_id INT AUTO_INCREMENT PRIMARY KEY,
    waktu_id INT NOT NULL,
    lokasi_id INT NOT NULL,
    curah_hujan DECIMAL(10, 2),          -- RR
    suhu_min DECIMAL(10, 2),             -- TN
    suhu_max DECIMAL(10, 2),             -- TX
    suhu_rata DECIMAL(10, 2),            -- TAVG
    kelembaban_rata DECIMAL(10, 2),      -- RH_AVG
    lama_penyinaran DECIMAL(10, 2),      -- SS
    kecepatan_angin_max DECIMAL(10, 2),  -- FF_X
    arah_angin_max VARCHAR(10),          -- DDD_X
    kecepatan_angin_rata DECIMAL(10, 2), -- FF_AVG
    arah_angin_terbanyak VARCHAR(10),    -- DDD_CAR
    FOREIGN KEY (waktu_id) REFERENCES DimWaktu(waktu_id),
    FOREIGN KEY (lokasi_id) REFERENCES DimLokasi(lokasi_id)
);

-- Insert data lokasi
INSERT INTO DimLokasi (nama_lokasi, jenis_lokasi) VALUES
('Bogor', 'Kabupaten'),
('Cirebon', 'Kabupaten'),
('Majalengka', 'Kabupaten'),
('Bandung', 'Kota'),
('Bogor', 'Kota');