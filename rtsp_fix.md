# FIX MASALAH RTSP BUFFERING

## Masalah:
- RTSP camera hanya membaca 1 frame pertama
- Semua pembacaan berikutnya gagal ("Frame read failed or frame is None")
- Browser menampilkan video "stack" / freeze

## Penyebab:
1. Buffer RTSP terlalu besar
2. Backend OpenCV tidak optimal untuk RTSP
3. Timeout read frame terlalu pendek

## Solusi yang sudah diterapkan:
1. ✅ `CAP_PROP_BUFFERSIZE, 1` - Kurangi buffering
2. ✅ `CAP_PROP_FOURCC` - MJPG codec
3. ✅ Backend FFmpeg (default di Linux)

## Perbaikan Tambahan:
1. Tambahkan timeout saat read kamera (5 detik)
2. Tambahkan retry mechanism (coba ulang jika gagal 3 kali)
3. Tambahkan reconnect logic jika banyak gagal beruntun
4. Lower buffer size menjadi 0 (no buffer)
5. Set RTSP transport jika tersedia

## Cara Testing:
1. Jalankan: `source venv/bin/activate && timeout 15 python3 -u web_server.py`
2. Buka browser: `http://YOUR_SERVER_IP:8080`
3. Cek log untuk melihat apakah masih ada "Frame read failed"
4. Jika masih ada masalah, kamera mungkin butuh restart
