# Situs STIKES Medika Seramoe Barat

## Pasang di GitHub (sekali saja)
1. Buat repo baru di GitHub (publik).
2. Unggah **seluruh isi** folder ini ke repo, termasuk folder `.github` dan file `.nojekyll`.
   Cara termudah: di komputer, `git init`, `git add .`, `git commit`, `git push`.
   (Unggah lewat browser sering melewatkan folder berawalan titik; kalau terjadi, buat
   `.github/workflows/pages.yml` manual lewat Add file → Create new file.)
3. Settings → Pages → Source → **GitHub Actions**.
4. Buka tab Actions, tunggu proses hijau. Situs aktif di `https://USERNAME.github.io/NAMA-REPO/`.

## Buat token admin
GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens →
Generate new token. Repository access: hanya repo ini. Permissions → Contents: **Read and write**.

## Mengelola isi
Buka `https://USERNAME.github.io/NAMA-REPO/admin/`, masuk dengan token, ubah isi, lalu tekan **Simpan**.
Situs diperbarui 1–2 menit kemudian.

## Isi folder
- `index.html` — beranda (membaca `data/content.json`)
- `data/content.json` — semua isi situs
- `halaman.html` + `generate_pages.py` — pembuat halaman prodi, berita, galeri, artikel
- `admin/` — panel admin
- `.github/workflows/pages.yml` — generate halaman dan deploy otomatis
- `berita/`, `prodi/`, `galeri/`, `pages.json` — hasil generate (dibuat ulang tiap deploy)
- `artikel/*.json` — isi lengkap tiap berita
