from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from models import UserCreate, UserLogin, UserResponse, SessionCreate, SessionResponse, UserWithSessionsResponse, InternalUserResponse
from database import create_user, get_user, create_session, get_sessions, upload_file_to_session, create_vector_store, start_thread, get_session_by_id, sessions_db
from pydantic import EmailStr
from typing import List
import bcrypt

app = FastAPI()

@app.post("/create_user", response_model=UserResponse)
def create_user_endpoint(user: UserCreate):
    if get_user(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    create_user(user)
    return UserResponse(
        email=user.email,
        phone=user.phone,
        company_name=user.company_name
    )

@app.post("/login", response_model=UserWithSessionsResponse)
def login(user: UserLogin):
    db_user = get_user(user.email)
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    sessions = get_sessions(user.email)
    return UserWithSessionsResponse(
        email=db_user.email,
        phone=db_user.phone,
        company_name=db_user.company_name,
        sessions=sessions
    )

@app.post("/create_session", response_model=SessionResponse)
def create_session_endpoint(session: SessionCreate, email: EmailStr = Query(...)):
    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_session = create_session(email, session)
    return new_session

@app.post("/upload_file/{session_id}", response_model=SessionResponse)
def upload_file_to_session_endpoint(session_id: int, file: UploadFile = File(...)):
    session = upload_file_to_session(session_id, file)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/run/{session_id}", response_model=SessionResponse)
def run_session_endpoint(session_id: int):
    session = get_session_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    file_path = session.get('file_path')
    if not file_path:
        raise HTTPException(status_code=400, detail="No file uploaded for this session")

    # Create vector store
    vector_store_id = create_vector_store(session_id, file_path)
    session['vector_store_id'] = vector_store_id

    # Start a new thread
    thread_id = start_thread(session_id)
    session['thread_id'] = thread_id

    # Update session in database
    for s in sessions_db:
        if s['id'] == session_id:
            s['vector_store_id'] = vector_store_id
            s['thread_id'] = thread_id

    return SessionResponse(**session)

@app.get("/sessions", response_model=List[SessionResponse])
def list_sessions(email: EmailStr = Query(...)):
    user = get_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    sessions = get_sessions(email)
    return sessions

@app.get("/")
def read_root():
    return {"message": "Welcome to the multi-user application. Please login or create a new user."}
