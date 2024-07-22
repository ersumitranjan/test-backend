from flask import Flask, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from models import db, User, File
from utils import generate_token, send_verification_email
import jwt
import os

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

# Create the tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    return "This the Test for backend!"

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    token = generate_token(user.id)
    send_verification_email(email, token)
    return jsonify({"verification_url": f"http://localhost:5000/api/verify-email?token={token}"}), 201

@app.route('/api/verify-email', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded['user_id']
        user = User.query.get(user_id)
        if user:
            user.verified = True
            db.session.commit()
            return jsonify({"message": "Email verified successfully"}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        token = generate_token(user.id)
        return jsonify({"token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        # Assuming user_id is fetched from JWT token
        user_id = 1  # Replace with actual user_id from JWT
        new_file = File(filename=filename, filepath=filepath, owner_id=user_id)
        db.session.add(new_file)
        db.session.commit()
        return jsonify({"message": "File uploaded successfully"}), 201
    return jsonify({"message": "Invalid file type"}), 400

@app.route('/api/download-file/<file_id>', methods=['GET'])
def download_file(file_id):
    # Check permissions and generate an encrypted URL
    file = File.query.get(file_id)
    if file:
        # Generate an encrypted URL for downloading
        download_link = f"http://localhost:5000/download/{file_id}"
        return jsonify({"download_link": download_link, "message": "success"}), 200
    return jsonify({"message": "File not found"}), 404

@app.route('/api/files', methods=['GET'])
def list_files():
    files = File.query.all()
    file_list = [{"file_id": file.id, "file_name": file.filename} for file in files]
    return jsonify({"files": file_list}), 200

if __name__ == '__main__':
    app.run(debug=True)
 
