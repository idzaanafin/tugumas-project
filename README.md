# tugumas-project


## Setup Project
### Install dependencies
```
pip install -r requirements.txt
```

### Environment Variable
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/tugumas
SECRET_KEY=your_secret_key
```

## Database
### Setup Database
```
CREATE DATABASE tugumas;
```
---
### Membuat migration

```bash
flask --app run db init
flask --app run db migrate -m "Initial migration"
```
---
### Run migration
```
flask --app run db upgrade
```
---
### Run seeder
```
python3 -m app.database.seed
```

---
### Membuat migration baru

Setelah ada perubahan model.

```bash
flask --app run db migrate -m "your migration message"
```
---
### Run migration ulang
```
flask --app run db upgrade
```
---

### Reset Database

- Rollback seluruh migration.

    ```bash
    flask --app run db downgrade base
    ```

- Recreate tabel.

    ```bash
    flask --app run db upgrade
    ```

- Run Seeder

    ```bash
    python3 -m app.database.seed
    ```



## Employee Attendance
Masukkan id pegawai dan nama pegawai dalam format json ke dalam file `employee_mapping.json`. Contoh format json:

```json
{
 "nama":"uuid",
}
```

### QR Code Generator
Jalankan perintah berikut untuk membuat QR Code absensi pegawai
```
cd ./scanner/
python3 generate-qr.py
```

### Face ID Recognition
Jalankan perintah berikut untuk membuat Face ID Recognition pegawai. Pastikan sudah menambahkan foto dengan nama file adalah nama pegawai yang ada di `employee_mapping.json` ke dalam folder `dataset_wajah`. Contoh: `dataset_wajah/nama.png`

```
cd ./scanner/
python3 register_faces.py
```

## Run Development Server

### Dashboard
pastikan database sudah di setup dan menjalankan migration beserta seeding database. Jalankan perintah berikut untuk menjalankan development server.
```
cd ./web-dashboard
python3 run.py
```
Akses melalui browser dengan alamat `http://localhost:5000/` untuk melihat dashboard.

Default username dan password untuk login ke dashboard adalah:
```
username: admin
password: tmoadmin123
```

### Scanner
Setelah mendaftarkan data wajah atau generate QR Code, jalankan perintah berikut untuk menjalankan scanner.
```
cd ./scanner
python3 app.py
```

Akses melalui browser dengan alamat 
 - `http://localhost:5001/` untuk QR Code scanner.
 - `http://localhost:5001/face` untuk Face ID scanner.


## Run Production Server
### Build & Jalankan Docker Container
```
docker compose up -d --build
```
### Setup Database Production
```
docker compose exec web-dashboard flask db init
docker compose exec web-dashboard flask db migrate -m "Initial migration"
docker compose exec web-dashboard flask db upgrade
docker compose exec web-dashboard python -m app.database.seed
```

### Mematikan Docker Container
```
docker compose down
```

### Restart Docker Container
```
docker compose restart
```

## Tips
- Konfigurasi firewall untuk mengizinkan akses ke port 5000 dan 5001.
- tambahkan .bat script untuk membuka url scanner pada browser secara otomatis.