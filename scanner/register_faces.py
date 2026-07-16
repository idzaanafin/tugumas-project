import json
import os

import face_recognition

from app import app, db, FaceRecord

# Folder dataset wajah
DATASET_FOLDER = "dataset_wajah"

# File mapping nama -> employee_id
MAPPING_FILE = "employee_mapping.json"


def load_employee_mapping():
    """Memuat mapping nama file -> employee_id."""
    if not os.path.exists(MAPPING_FILE):
        print(f"❌ File '{MAPPING_FILE}' tidak ditemukan.")
        return {}

    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def process_and_save_faces():
    if not os.path.exists(DATASET_FOLDER):
        os.makedirs(DATASET_FOLDER)
        print(f"📁 Folder '{DATASET_FOLDER}' dibuat.")
        print("Silakan masukkan foto pegawai ke dalam folder tersebut.")
        return

    employee_mapping = load_employee_mapping()

    if not employee_mapping:
        print("❌ Mapping pegawai kosong.")
        return

    # Menjalankan di dalam context Flask agar bisa akses database
    with app.app_context():
        db.create_all()

        for filename in os.listdir(DATASET_FOLDER):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            image_path = os.path.join(DATASET_FOLDER, filename)

            # Nama file tanpa ekstensi
            employee_name = os.path.splitext(filename)[0]

            # Cari employee_id berdasarkan mapping
            employee_id = employee_mapping.get(employee_name)

            if employee_id is None:
                print(
                    f"❌ SKIP: '{employee_name}' belum ada di '{MAPPING_FILE}'."
                )
                continue

            print(f"🔄 Memproses: {filename}")

            try:
                # Load gambar
                image = face_recognition.load_image_file(image_path)

                # Deteksi wajah
                face_locations = face_recognition.face_locations(
                    image,
                    model="hog"
                )

                if len(face_locations) == 0:
                    print("   ❌ Tidak ada wajah terdeteksi.")
                    continue

                if len(face_locations) > 1:
                    print("   ⚠️ Terdapat lebih dari satu wajah. Menggunakan wajah pertama.")

                # Generate encoding
                encoding = face_recognition.face_encodings(
                    image,
                    face_locations
                )[0]

                encoding_json = json.dumps(encoding.tolist())

                # Simpan / update database
                existing_record = FaceRecord.query.filter_by(
                    employee_id=employee_id
                ).first()

                if existing_record:
                    existing_record.encoding = encoding_json
                    print(f"   ✅ UPDATE: {employee_name}")
                else:
                    db.session.add(
                        FaceRecord(
                            employee_id=employee_id,
                            encoding=encoding_json
                        )
                    )
                    print(f"   ✅ REGISTER: {employee_name}")

            except Exception as e:
                print(f"   ❌ ERROR: {e}")

        db.session.commit()

    print("\n🎉 Registrasi wajah selesai.")


if __name__ == "__main__":
    process_and_save_faces()
