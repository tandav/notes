from notes_v2.database import SessionLocal, engine
from notes_v2.util import MediaType
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

def get_db():
    db = SessionLocal()
    yield db
    db.close()

http_basic = HTTPBasic()
http_basic_optional = HTTPBasic(auto_error=False)

def guess_tupe():
    return MediaType
