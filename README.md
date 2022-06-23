# 1. monitax
Backend untuk aplikasi monitoring pajak online

Dibangun menggunakan framework FastAPI  dan SQLModel

# TODO:
- [x] User management
- [x] Device management
- [x] Task worker (Celery)
- [ ] Role dan permission
- [ ] Dashboard

Dari directori root project, jalankan perintah berikut:
``` 
uvicorn app.main:app--reload --port 8008
