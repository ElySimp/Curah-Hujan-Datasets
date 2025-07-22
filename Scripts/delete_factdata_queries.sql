-- ===== SQL COMMANDS UNTUK MENGHAPUS DATA FACTDATAIKLIM =====

-- 1. HAPUS SEMUA DATA (HATI-HATI!)
DELETE FROM FactDataIklim;

-- 2. HAPUS DATA BERDASARKAN LOKASI TERTENTU
-- Contoh: Hapus data Majalengka saja
DELETE f FROM FactDataIklim f
JOIN DimLokasi l ON f.lokasi_id = l.lokasi_id
WHERE l.nama_lokasi = 'Majalengka' AND l.jenis_lokasi = 'Kabupaten';

-- 3. HAPUS DATA BERDASARKAN TAHUN TERTENTU
-- Contoh: Hapus data tahun 2024
DELETE f FROM FactDataIklim f
JOIN DimWaktu w ON f.waktu_id = w.waktu_id
WHERE w.tahun = 2024;

-- 4. HAPUS DATA BERDASARKAN RANGE TANGGAL
-- Contoh: Hapus data bulan Januari 2024
DELETE f FROM FactDataIklim f
JOIN DimWaktu w ON f.waktu_id = w.waktu_id
WHERE w.tanggal BETWEEN '2024-01-01' AND '2024-01-31';

-- 5. HAPUS DATA BERDASARKAN LOKASI DAN TAHUN
-- Contoh: Hapus data Majalengka tahun 2024 saja
DELETE f FROM FactDataIklim f
JOIN DimLokasi l ON f.lokasi_id = l.lokasi_id
JOIN DimWaktu w ON f.waktu_id = w.waktu_id
WHERE l.nama_lokasi = 'Majalengka' 
  AND l.jenis_lokasi = 'Kabupaten'
  AND w.tahun = 2024;

-- 6. HAPUS DATA MULTIPLE LOKASI
-- Contoh: Hapus data Bogor Kabupaten dan Kota
DELETE f FROM FactDataIklim f
JOIN DimLokasi l ON f.lokasi_id = l.lokasi_id
WHERE l.nama_lokasi = 'Bogor';

-- 7. CEK JUMLAH DATA SEBELUM HAPUS (REKOMENDASI)
-- Selalu check dulu sebelum delete
SELECT COUNT(*) as total_records FROM FactDataIklim;

-- CEK DATA PER LOKASI
SELECT 
    l.nama_lokasi,
    l.jenis_lokasi,
    COUNT(*) as total_records
FROM FactDataIklim f
JOIN DimLokasi l ON f.lokasi_id = l.lokasi_id
GROUP BY l.nama_lokasi, l.jenis_lokasi
ORDER BY l.nama_lokasi;

-- 8. RESET AUTO_INCREMENT (OPSIONAL)
-- Setelah delete semua data, reset ID counter
ALTER TABLE FactDataIklim AUTO_INCREMENT = 1;

-- ===== PERINGATAN PENTING =====
-- 1. SELALU BACKUP DATABASE SEBELUM DELETE!
-- 2. Gunakan WHERE clause untuk menghindari delete semua data
-- 3. Test dengan SELECT dulu sebelum DELETE
-- 4. Pertimbangkan menggunakan TRUNCATE TABLE untuk delete semua data lebih cepat

-- CONTOH TEST SEBELUM DELETE:
-- Ganti DELETE dengan SELECT untuk test dulu
SELECT f.*, l.nama_lokasi, w.tanggal
FROM FactDataIklim f
JOIN DimLokasi l ON f.lokasi_id = l.lokasi_id
JOIN DimWaktu w ON f.waktu_id = w.waktu_id
WHERE l.nama_lokasi = 'Majalengka' AND l.jenis_lokasi = 'Kabupaten'
LIMIT 10;

-- TRUNCATE (HAPUS SEMUA DATA LEBIH CEPAT)
-- HATI-HATI: Ini akan hapus SEMUA data dan reset AUTO_INCREMENT
TRUNCATE TABLE FactDataIklim;
