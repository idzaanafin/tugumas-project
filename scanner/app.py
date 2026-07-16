import base64
import json
import numpy as np
import cv2
import face_recognition
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scanner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 1. MODEL
class FaceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(36), unique=True, nullable=False)
    encoding = db.Column(db.Text, nullable=False)

KNOWN_FACES = []
KNOWN_EMPLOYEE_IDS = []

# 2. LOAD DATASET
def load_known_faces():
    global KNOWN_FACES, KNOWN_EMPLOYEE_IDS
    KNOWN_FACES.clear()
    KNOWN_EMPLOYEE_IDS.clear()
    
    with app.app_context():
        db.create_all()
        records = FaceRecord.query.all()
        for record in records:
            KNOWN_FACES.append(np.array(json.loads(record.encoding)))
            KNOWN_EMPLOYEE_IDS.append(record.employee_id)
            
    print(f"[*] Scanner AI siap: Memuat {len(KNOWN_FACES)} wajah ke memori.")

load_known_faces()

# 3. ROUTING 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/face')
def face_scanner():
    return render_template('face_scanner.html')

# 4. SCANNER
@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.get_json()
    image_base64 = data.get('image')
    
    try:
        image_data = image_base64.split(",")[1] if "," in image_base64 else image_base64
        img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_img, model="hog")
        if not face_locations:
            return jsonify({"status": "ignored", "message": "Tidak ada wajah"}), 200
            
        unknown_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
        
        if len(KNOWN_FACES) == 0:
            return jsonify({"status": "ignored", "message": "Database kosong"}), 200

        face_distances = face_recognition.face_distance(KNOWN_FACES, unknown_encoding)
        best_match_index = np.argmin(face_distances)
        
        if face_distances[best_match_index] <= 0.5:
            return jsonify({
                "status": "success",
                "employee_id": KNOWN_EMPLOYEE_IDS[best_match_index],
                "confidence": round((1 - face_distances[best_match_index]) * 100, 2)
            }), 200
        else:
            return jsonify({"status": "ignored", "message": "Wajah tidak dikenali"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
