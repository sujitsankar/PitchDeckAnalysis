from pydantic import EmailStr
from models import UserCreate, SessionCreate, SessionResponse, InternalUserResponse
import bcrypt
import os

# Mocking a simple in-memory database using a dictionary for demonstration purposes
users_db = {}
sessions_db = []
files_db = {}

def create_user(user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    user_data = user.dict()
    user_data['password'] = hashed_password
    users_db[user.email] = user_data

def get_user(email: EmailStr):
    user_data = users_db.get(email)
    if not user_data:
        return None
    return InternalUserResponse(
        email=user_data['email'],
        phone=user_data['phone'],
        company_name=user_data['company_name'],
        password=user_data['password']
    )

def create_session(email: EmailStr, session: SessionCreate):
    new_session = {
        'id': len(sessions_db) + 1,
        'session_name': session.session_name,
        'user_email': email,
        'file_path': None  # Initially no file is uploaded
    }
    sessions_db.append(new_session)
    return SessionResponse(**new_session)

def get_sessions(email: EmailStr):
    return [SessionResponse(**session) for session in sessions_db if session['user_email'] == email]

def upload_file_to_session(session_id: int, file):
    session = next((s for s in sessions_db if s['id'] == session_id), None)
    if not session:
        return None
    file_path = f"uploads/{session_id}_{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    session['file_path'] = file_path
    return SessionResponse(**session)
