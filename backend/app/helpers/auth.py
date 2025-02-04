# import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError, conset
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

from db import SessionLocal
# from sqlalchemy.
from models import User

load_dotenv()

# Token URL, where the client (e.g., frontend) will send credentials to get the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Reuse SECRET_KEY and ALGORITHM
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

def get_password_hash(password: str):
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Create a JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create an access token with expiration."""
    to_encode = data.copy()
    
    # Set expiration time for access token
    expire = datetime.now() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create a refresh token with longer expiration."""
    to_encode = data.copy()
    
    # Set expiration time for refresh token
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode(token, KEY):
    return jwt.decode(token, KEY, algorithms=[ALGORITHM])

def decode_access_token(token):
    return decode(token, SECRET_KEY)

def decode_refresh_token(token):
    return decode(token, REFRESH_SECRET_KEY)

# Function to decode and verify JWT token
def verify_token(token: str):
    db = SessionLocal()

    try:
        # Decode the JWT token
        payload = decode_access_token(token)
        expiry = datetime.fromtimestamp(payload.get('exp'))
        
        if(expiry > datetime.now()):
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # return username  # Return the username extracted from the token
            return db.query(User).filter(User.username == username).first()
        else:
            raise HTTPException(status_code=440, detail="Session Timed Out!")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    finally:
        db.close()

# Dependency to get the current user based on the token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)

