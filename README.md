# MONITAX
Backend untuk aplikasi monitoring pajak online

Dibangun menggunakan framework FastAPI  dan SQLModel

# TODO:
- [x] User management
- [x] Device management
- [ ] Task worker (Celery)
- [ ] Role dan permission
- [ ] Dashboard

# How to
- Clone this repository

- Dari direktori root project, jalankan perintah berikut:
```
$ pip install -r requirements.txt
```
Lebih baik dijalankan dalam sebuah virtual environment (python 3.10+)

Atau bila ingin menggunakan poetry, jalankan perintah berikut di terminal
```
$ poetry install
```
- Di direktori root project ada file contoh untuk environment (*env.example*). Rename file menjadi .env
kemudian ubah variabel sesuai kebutuhan.

Untuk migrasi menggunakan alembic (Postgresql database) dan sekaligus inisialisasi data jalankan perintah berikut
```
$ bash init.sh
```
# Using Docker
Jalankan perintah berikut di terminal
```
$ docker-compose up -d
```

