from fastapi.security import HTTPBearer
from fastapi import HTTPException, Depends
from src.Auths.auth import verify_token

security = HTTPBearer()

def isLogin(token=Depends(security)):
    data = verify_token(token.credentials)
    if not data:
        raise HTTPException(401, detail="Invalid token")
    
    return data