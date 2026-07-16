import qrcode
import os
import json

with open("employee_mapping.json", "r", encoding="utf-8") as f:
    MOCK_DATABASE = json.load(f)

def generate_qr_codes():    
    output_dir = "data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Memulai proses generate QR Code...\n")
    
    for nama, id_pegawai in MOCK_DATABASE.items():        
        qr = qrcode.QRCode(
            version=1, # Ukuran QR (1 paling kecil)
            error_correction=qrcode.constants.ERROR_CORRECT_H, # Toleransi error tinggi
            box_size=10, # Ukuran pixel tiap kotak
            border=4, # Ketebalan border putih
        )
        qr.add_data(id_pegawai)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
                
        nama_file = f"{id_pegawai}_{nama.replace(' ', '_')}.png"
        path_file = os.path.join(output_dir, nama_file)
        img.save(path_file)
        print(f"[SUCCESS] QR Code dibuat: {path_file}")

if __name__ == "__main__":
    generate_qr_codes()
    print("\nSemua QR code selesai dibuat")
