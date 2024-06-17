import os
import threading
from openai import OpenAI  # Assuming you're using the OpenAI API client
from models import UserCreate, SessionCreate, SessionResponse, InternalUserResponse
from pydantic import EmailStr
import bcrypt

# Mocking a simple in-memory database using a dictionary for demonstration purposes
users_db = {}
sessions_db = []
files_db = {}

openai_client = OpenAI(api_key="sk-proj-b5eN4SYS7pb5cW7SPivGT3BlbkFJstPnEEUcIuAwik4m43rn")  # Initialize your OpenAI client here

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
        'file_path': None,  # Initially no file is uploaded
        'vector_store_id': None,
        'thread_id': None
    }
    sessions_db.append(new_session)
    return SessionResponse(**new_session)

def get_sessions(email: EmailStr):
    return [SessionResponse(**session) for session in sessions_db if session['user_email'] == email]

def upload_file_to_session(session_id: int, file):
    session = get_session_by_id(session_id)
    if not session:
        return None
    file_path = f"uploads/{session_id}_{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    session['file_path'] = file_path
    return SessionResponse(**session)

def create_vector_store(session_id: int, file_path: str):
    session = get_session_by_id(session_id)
    if not session:
        return None

    # Create a vector store using the OpenAI API
    vector_store = openai_client.beta.vector_stores.create(name=session['session_name'])
    session['vector_store_id'] = vector_store.id

    # Save the vector store ID to the session
    for s in sessions_db:
        if s['id'] == session_id:
            s['vector_store_id'] = vector_store.id

    return vector_store.id

def start_thread(session_id: int):
    session = get_session_by_id(session_id)
    if not session:
        return None

    def thread_task():
        # Start a new thread using the OpenAI API
        thread = openai_client.beta.threads.create()
        session['thread_id'] = thread.id

        # Save the thread ID to the session
        for s in sessions_db:
            if s['id'] == session_id:
                s['thread_id'] = thread.id

        print(f"Thread started for session {session_id}")

    thread = threading.Thread(target=thread_task)
    thread.start()
    thread.join()  # Ensure the thread completes before proceeding

    return session['thread_id']

def get_session_by_id(session_id: int):
    return next((s for s in sessions_db if s['id'] == session_id), None)
