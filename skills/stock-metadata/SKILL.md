---
name: stock-metadata
description: >-
  Periksa, bersihkan, dan optimasi metadata stock (Title & Keywords) pada file CSV untuk
  marketplace aset stock seperti Adobe Stock dan Vecteezy, termasuk aset Generative AI
  (video maupun gambar). WAJIB gunakan skill ini setiap kali user mengunggah atau menyebut
  file CSV metadata stock, atau meminta untuk: memeriksa/membersihkan/mengoptimasi title dan
  keyword, melaporkan pelanggaran IP/brand/keyword terlarang/keyword stuffing/over-limit,
  menghapus jejak proses AI dari metadata, menyiapkan metadata untuk diunggah ke Adobe Stock
  atau Vecteezy — BAHKAN bila kata "skill" tidak disebut. Pemicu meliputi: CSV berkolom
  Filename/Title/Keywords, frasa "metadata stock", "optimasi keyword", "cek CSV", "bersihkan
  keyword AI", "review metadata aset", "siapkan untuk Vecteezy/Adobe Stock".
---

# Optimasi Metadata Stock (Multi-Platform)

Skill untuk memeriksa, membersihkan, dan mengoptimasi `Title` dan `Keywords` pada file CSV
metadata untuk marketplace stock. Mendukung beberapa platform via profil (lihat
`references/platforms.json`); saat ini: **Adobe Stock** dan **Vecteezy**. Berlaku untuk semua
jenis aset (realistic, abstract, 3D, CGI, illustration, lifestyle, nature, beauty, food,
interior, science, dll), dengan perhatian khusus pada aset Generative AI: semua jejak proses
pembuatan AI harus hilang dari metadata.

## Prinsip inti

Pekerjaan terbagi dua, dan masing-masing dikerjakan pihak yang paling andal:

1. **Mekanis** (hitung karakter/kata/keyword, deteksi duplikat & istilah terlarang, lowercase,
   dehyphen) -> `scripts/validate_clean.py`. Jangan menghitung manual; jalankan script.
2. **Penilaian** (apakah title sesuai visual, istilah IP mana yang diganti & apa penggantinya,
   urutan relevansi keyword) -> Claude. Ini butuh pemahaman, bukan aturan kaku.

## Mode CSV-saja (penting)

File CSV **tidak berisi gambar**. "Visual aset" hanya tersirat dari gabungan Title + Keywords
yang sudah ada. Karena itu:

- **Jangan pernah mengarang detail visual baru** yang tidak didukung metadata asli (warna,
  objek, setting yang tidak disebut di mana pun). Bekerjalah dari yang ada.
- Tugasmu: buat metadata itu akurat, ringkas, aman, dan terurut kuat -- bukan menambah klaim.
- Jika sebuah baris metadatanya terlalu miskin untuk dinilai, katakan terus terang dan minta
  user melengkapi, daripada menebak.

## Alur kerja

### 1. Tentukan platform

Tanyakan atau simpulkan platform target (Adobe Stock atau Vecteezy). Jika user tidak menyebut
dan tidak bisa disimpulkan dari konteks, **tanyakan dulu** -- karena limit & aturan title
berbeda. Lihat `references/platforms.json` untuk profil yang tersedia.

### 2. Jalankan gerbang deterministik

```bash
python scripts/validate_clean.py <input.csv> --platform <adobe_stock|vecteezy> \
  --out <input>.cleaned.csv --report <input>.report.json
```

Menghasilkan CSV yang sudah dibersihkan mekanis + laporan JSON per baris. Script: hitung
panjang/kata Title & jumlah keyword (sesuai limit platform), hapus istilah AI/tool/proses,
dehyphen, lowercase kecuali akronim, buang duplikat & keyword kosong, tandai kata title yang
tidak disarankan platform, dan **menandai** istilah berisiko IP untuk kamu tinjau. Kolom
`Filename`, `Category`, `Releases` tidak disentuh.

### 3. Laporkan temuan

Baca `report.json`. Sajikan ringkasan per kategori dengan referensi `Filename`:
IP/brand/trademark; nama orang/karakter; landmark/lokasi spesifik; editorial/institusi/
event; konten sensitif/klaim medis; istilah AI/tool (sudah dihapus -- laporkan saja);
teknis title; teknis keyword; keyword stuffing/spekulatif/tidak relevan.

**Penting soal istilah yang ditandai (flag_for_review):** banyak brand berupa kata umum
(apple, dove, shell, corona, polo, jaguar, puma, subway, visa). Nilai per konteks: jika jelas
merujuk benda umum (buah apel, burung dara) dan bukan brand, **biarkan**. Hanya ganti bila
benar-benar merujuk merek/IP terproteksi.

### 4. Optimasi penilaian per baris

Terapkan aturan TITLE (sesuai platform), KEYWORD, dan GANTI-IP di bawah. Baris yang sudah
bersih dan tidak melanggar **biarkan apa adanya** -- jangan menulis ulang tanpa alasan.

### 5. Kembalikan hasil

- File **CSV final siap unggah** (gunakan tool file / `present_files`); tawarkan fenced CSV
  bila diminta.
- **Ringkasan perubahan** ringkas + contoh before/after 2-3 baris yang paling berubah.
- Jangan ubah `Filename`, `Category`, `Releases`.

## Aturan TITLE (sesuai platform)

Tulis ulang hanya jika melanggar/lemah. Hindari title generik kosong ("Loop", "Abstract
Background") kecuali itu memang deskripsi terjujur. Jangan mengesankan aset sintetis sebagai
dokumentasi dunia nyata bila tidak jelas. **Dilarang keras di semua platform:** "Generative
AI", "AI", nama model/tool AI, istilah prompt, klaim teknis proses produksi.

**Adobe Stock:** Title Case, deskriptif, ideal 70-100 char (maks 200). Pola:
`[subjek utama] + [deskriptor/aksi] + [setting/konteks]`.
Contoh: `Glowing Blue Neon Light Flowing in Seamless Motion on a Dark Background`

**Vecteezy:** ringkas **3-8 kata, di bawah 70 karakter**, profesional & gramatikal.
**Jangan** masukkan kata resolusi/teknis ("4K", "footage", "video", "HD") atau adjektiva
subjektif ("beautiful", "amazing", "stunning", "perfect") -- script menandainya.
Contoh: `Neon Light Flowing on Dark Background`

Jika title over-limit, pangkas dari klausa ekor, jangan buang subjek utamanya.

## Aturan KEYWORD

- Lowercase kecuali akronim umum (CGI, DNA, mRNA, 3D, 4K, dll) -- ditangani script.
- **Urutkan dari paling relevan ke paling lemah** sebagai langkah eksplisit. Keyword awal
  diberi bobot lebih oleh pencarian: **Adobe Stock = 10 teratas**, **Vecteezy = 5 teratas**.
- **Heuristik urutan:** (1) subjek utama, (2) elemen visual menonjol, (3) setting/environment,
  (4) material/tekstur/warna/lighting, (5) mood/konsep relevan, (6) istilah teknis/gaya
  (loop, seamless, animation, CGI, 3D render, motion graphics) **paling akhir & hanya bila
  benar-benar sesuai**.
- **Limit:** Adobe Stock maks 49; Vecteezy maks 50 (disarankan ~20-30, minimum 5). Jika
  setelah diurutkan masih melebihi, pangkas dari ekor.
- **Pangkas yang lemah** meski belum mencapai limit: buang keyword spekulatif, terlalu generik,
  atau tidak didukung metadata. Presisi > panjang. Jangan paksakan paket keyword seragam.
- Vecteezy: aturan **satu bentuk per kata** kini otomatis -- script menggabungkan pasangan
  singular/plural yang muncul bersamaan (mis. flower+flowers, child+children) dan
  mempertahankan kemunculan pertama. Untuk pasangan ambigu yang bermakna beda (mis.
  glass/glasses, arm/arms) script TIDAK menggabung tapi menandainya
  `kemungkinan_bentuk_ganda_perlu_cek` -- tinjau dan putuskan secara manual.

## Gerbang keamanan Generative AI

Ditegakkan otomatis (lihat `references/banned_terms.json`), tapi tetap periksa: tidak boleh
ada nama model/tool (Midjourney, Firefly, DALL-E, Sora, Stable Diffusion, Runway, dll),
istilah proses (prompt, upscale, seed, text to image, render engine), nama artist/studio,
atau frasa "in the style of ...". Selalu pilih deskripsi visual generik daripada referensi
spesifik berisiko IP.

## Tabel penggantian IP aman

Saat script menandai `flag_for_review` dan istilahnya memang merujuk merek/IP terproteksi:

| Ditemukan | Ganti dengan (contoh) |
|---|---|
| Brand/produk (Coca-Cola, iPhone) | "red soda can", "modern smartphone" |
| Landmark spesifik (Eiffel Tower) | "ornate iron lattice tower at dusk" |
| Nama orang nyata | "businesswoman", "young athlete" |
| Karakter/franchise | "cartoon superhero figure" |
| Nama artist / style artist | "impressionist style", "vibrant brushstrokes" |
| Lembaga (NASA, FBI) | "space agency style emblem", "investigator" |
| Event bermerek (Olympics) | "international sports event" |
| Klaim medis/kosmetik | netralkan: "skincare", "wellness"; buang "proven/cure" |

**Flag manual** (laporkan walau tak tertangkap script): nama bangunan modern berhak cipta
arsitektur, kata mirip brand, slogan/trade dress, klaim medis berlebihan.

## Format output

Pertahankan kolom asli (`Filename, Title, Keywords, Category, Releases`, dan kolom lain bila
ada). Keywords dipisah `, `. Output akhir = CSV lengkap (file unduhan), bukan cuplikan,
kecuali user minta sample.

## Merawat & memperluas

- Tambah nama tool AI / brand / istilah terlarang baru ke `references/banned_terms.json`.
- Tambah platform baru (Shutterstock, Freepik, Pond5, 123RF) dengan menyalin satu blok di
  `references/platforms.json` dan menyesuaikan limit + aturan title-nya. Tidak perlu mengubah
  script.
