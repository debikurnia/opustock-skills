# Berkontribusi

Terima kasih atas minatmu untuk berkontribusi! Koleksi ini sederhana secara struktur: **satu skill = satu folder di `skills/`**.

## Anatomi sebuah skill

```
skills/<nama-skill>/
├── SKILL.md            # wajib: frontmatter (name, description) + instruksi
├── scripts/            # opsional: kode untuk tugas deterministik
└── references/         # opsional: data/aturan yang dibaca script atau Claude
```

`SKILL.md` diawali frontmatter YAML:

```yaml
---
name: nama-skill
description: >-
  Apa yang dilakukan skill ini DAN kapan harus dipakai. Bagian ini adalah
  pemicu utama, jadi sebutkan konteks/frasa yang harus mengaktifkannya.
---
```

## Prinsip yang kami ikuti

1. **Pisahkan mekanis dari penilaian.** Kalau sesuatu bisa dihitung atau dicocokkan dengan andal, taruh di script. Sisakan penilaian (akurasi, relevansi, keamanan IP) untuk Claude.
2. **Aman secara default.** Saat ragu, tandai untuk ditinjau alih-alih menghapus diam-diam.
3. **Aturan sebagai data, bukan prosa.** Daftar (istilah terlarang, limit platform) tinggal di file `references/` agar mudah dirawat.
4. **Jelaskan "mengapa".** Instruksi yang menjelaskan alasannya lebih mudah diikuti dengan benar daripada deretan perintah kaku.

## Menambah skill baru

1. Fork repo & buat branch.
2. Buat folder `skills/<nama-skill>/` berisi minimal `SKILL.md`.
3. Uji secara lokal: install paket `.skill`-nya (`python scripts/build.py`) lalu coba di Claude dengan beberapa prompt realistis.
4. Perbarui daftar skill & roadmap di `README.md`.
5. Ajukan Pull Request dengan deskripsi singkat: apa yang dilakukan skill, kapan terpicu, dan bagaimana kamu mengujinya.

## Melaporkan masalah

Buka issue dengan contoh input (boleh disensor) dan hasil yang kamu harapkan vs yang kamu dapat.
