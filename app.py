from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_ops_user = db.Column(db.Boolean, default=False)  # True if the user is an Ops user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/')
def home():
    return 'This is test for Backend intern'

@app.route('/ops/login', methods=['POST'])
def ops_login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        if user.is_ops_user:
            access_token = create_access_token(identity={'email': user.email, 'is_ops_user': user.is_ops_user})
            return jsonify({"access_token": access_token}), 200
        else:
            return jsonify({"message": "Unauthorized: Not an Ops user"}), 403
    else:
        return jsonify({"message": "Invalid email or password"}), 401

@app.route('/ops/upload', methods=['POST'])
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

@app.route('/client/signup', methods=['POST'])
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


@app.route('/client/verify/<token>', methods=['GET'])
def verify_email(token):
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

@app.route('/client/login', methods=['POST'])
def client_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        token = generate_token(user.id)
        return jsonify({"token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/client/download/<file_id>', methods=['GET'])
def download_file(file_id):
    file = File.query.get(file_id)
    if file:
        # Generate an encrypted URL for downloading
        download_link = f"http://localhost:5000/download/{file_id}"
        return jsonify({"download_link": download_link, "message": "success"}), 200
    return jsonify({"message": "File not found"}), 404

@app.route('/client/files', methods=['GET'])
def list_files():
    files = File.query.all()
    file_list = [{"file_id": file.id, "file_name": file.filename} for file in files]
    return jsonify({"files": file_list}), 200

if __name__ == '__main__':
    app.run(debug=True)

