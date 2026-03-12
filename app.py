import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///notes.db')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user') # 'user' or 'admin'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- Authentication ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Missing username or password"}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "User already exists"}), 400

    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_pw, role=data.get('role', 'user'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and check_password_hash(user.password, data.get('password')):
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

# --- Notes Management, RBAC & Search ---
@app.route('/notes', methods=['GET', 'POST'])
@jwt_required()
def manage_notes():
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    if request.method == 'POST':
        data = request.get_json()
        if not data.get('title') or not data.get('content'):
            return jsonify({"msg": "Title and content required"}), 400
        new_note = Note(title=data['title'], content=data['content'], user_id=user_id)
        db.session.add(new_note)
        db.session.commit()
        return jsonify({"msg": "Note created"}), 201

    if request.method == 'GET':
        search_query = request.args.get('search')
        
        # Base query depends on role
        if claims.get('role') == 'admin':
            base_query = Note.query
        else:
            base_query = Note.query.filter_by(user_id=user_id)
            
        # Optional Enhancement: Search by title
        if search_query:
            base_query = base_query.filter(Note.title.ilike(f'%{search_query}%'))
            
        notes = base_query.all()
        
        return jsonify([{
            "id": n.id, "title": n.title, "content": n.content, 
            "created_at": n.created_at, "user_id": n.user_id
        } for n in notes]), 200

@app.route('/notes/<int:note_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def note_detail(note_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    note = Note.query.get_or_404(note_id)

    if note.user_id != user_id and claims.get('role') != 'admin':
        return jsonify({"msg": "Permission denied"}), 403

    if request.method == 'DELETE':
        db.session.delete(note)
        db.session.commit()
        return jsonify({"msg": "Note deleted"}), 200

    if request.method == 'PUT':
        data = request.get_json()
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        db.session.commit()
        return jsonify({"msg": "Note updated"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
