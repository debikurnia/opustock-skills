# Contoh

`sample_input.csv` adalah metadata mentah dengan beragam masalah yang umum ditemui:
istilah AI (`ai`, `generative ai`), nama tool (`Midjourney`), duplikat (`abstract`,
`neon`), tanda hubung (`anti-aging`), huruf besar (`FLOWER`), keyword kosong (koma di
akhir), landmark berisiko IP (`Eiffel Tower`), title generik (`Loop`), dan pasangan
singular/plural (`flower`/`flowers`).

Coba sendiri di Claude setelah meng-install skill `stock-metadata`:

> Unggah `sample_input.csv` dan minta: *"Periksa dan optimasi metadata ini untuk Adobe Stock"*
> atau *"...untuk Vecteezy"* — bandingkan perbedaan limit & aturannya.

Atau jalankan gerbang mekanisnya langsung:

```bash
python skills/stock-metadata/scripts/validate_clean.py examples/sample_input.csv --platform vecteezy
```
