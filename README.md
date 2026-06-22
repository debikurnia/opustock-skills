# Opustock Skills

> Koleksi [Claude Skills](https://www.anthropic.com/news/skills) untuk kontributor **microstock** — mengubah pekerjaan metadata yang membosankan dan rawan salah menjadi langkah satu-perintah yang konsisten, aman, dan siap unggah.

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Skills](https://img.shields.io/badge/skills-1-blue.svg)
![Platforms](https://img.shields.io/badge/platforms-Adobe%20Stock%20%7C%20Vecteezy-orange.svg)

Terinspirasi oleh pendekatan [obra/Superpowers](https://github.com/obra/Superpowers): sekumpulan skill kecil yang ter-*compose*, terpicu otomatis, dan punya satu tugas yang dikerjakan dengan baik. Bedanya, koleksi ini fokus pada satu domain — alur kerja **kontributor aset microstock**.

---

## Apa ini?

Setiap skill di sini adalah folder berisi `SKILL.md` (instruksi untuk Claude) ditambah script/data pendukung. Saat di-install, Claude memakainya **otomatis** begitu konteksnya cocok — kamu tidak perlu menyalin-tempel instruksi panjang lagi.

Prinsip desain di seluruh koleksi:

- **Mesin mengerjakan yang mekanis, Claude mengerjakan yang butuh penilaian.** Hal yang bisa dihitung/dicocokkan (jumlah karakter, duplikat, istilah terlarang) ditangani script secara 100% andal; sisanya yang butuh pemahaman (akurasi, keamanan IP, relevansi) ditangani Claude.
- **Aman secara default.** Lebih baik konservatif daripada agresif: kalau ragu, tandai untuk ditinjau, jangan hapus diam-diam.
- **Mudah dirawat & diperluas.** Aturan tinggal di file data, bukan terkubur dalam prosa.

## Daftar skill

### `stock-metadata`

Periksa, bersihkan, dan optimasi `Title` & `Keywords` pada file CSV metadata untuk **Adobe Stock** dan **Vecteezy** (termasuk aset Generative AI). Multi-platform lewat profil.

- Menghapus jejak proses AI & nama tool dari metadata.
- Menandai risiko IP/brand/landmark/karakter/editorial untuk ditinjau.
- Menegakkan limit per-platform (panjang title, jumlah keyword, kata title terlarang).
- Membersihkan tanda hubung, huruf besar, duplikat, dan keyword kosong.
- Khusus Vecteezy: menggabungkan bentuk singular/plural otomatis (aturan satu-bentuk-per-kata).

Detail di [`skills/stock-metadata/SKILL.md`](skills/stock-metadata/SKILL.md).

## Instalasi (Claude.ai / Claude Desktop)

1. Build paket `.skill`:
   ```bash
   python scripts/build.py
   ```
   File hasil ada di `dist/<nama-skill>.skill`.
2. Di Claude, buka **Settings → Capabilities → Skills → Upload skill**, lalu pilih file `.skill` tadi.
3. Selesai. Unggah CSV metadata-mu dan minta, mis. *"optimasi metadata ini untuk Vecteezy"* — skill akan aktif sendiri.

> Tidak ingin build? Setiap folder di `skills/` sudah merupakan skill lengkap; kamu bisa men-zip foldernya sendiri menjadi `.skill` (zip biasa).

## Contoh

Lihat folder [`examples/`](examples/) untuk CSV contoh sebelum/sesudah optimasi.

## Roadmap

Skill pendukung yang direncanakan untuk koleksi ini:

- [ ] **Dukungan platform tambahan** — Shutterstock, Freepik, Pond5, 123RF (tinggal menambah profil).
- [ ] **keyword-research** — menyarankan keyword bernilai-cari dari subjek aset.
- [ ] **batch-rename** — penamaan file aset yang konsisten dan rapi.
- [ ] **csv-merge** — menggabungkan/mencocokkan beberapa ekspor metadata.
- [ ] **release-tracker** — melacak model/property release per aset.

Punya ide? Buka issue.

## Kontribusi

Lihat [CONTRIBUTING.md](CONTRIBUTING.md). Singkatnya: satu skill = satu folder di `skills/` berisi `SKILL.md`.

## Lisensi

[MIT](LICENSE) © 2026 Debi Kurnia

## Penulis

**Debi Kurnia** — kontributor microstock & pembuat tooling.
GitHub: [@debikurnia](https://github.com/debikurnia)

Jika koleksi ini membantu alur kerjamu, beri ⭐ pada repo ini.
