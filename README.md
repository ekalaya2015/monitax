# 1. monitax
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

Untuk migrasi menggunakan alembic (Postgresql database), jalankan perintah berikut di terminal
```
$ alembic upgrade head
```


