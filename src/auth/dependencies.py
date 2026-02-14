from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.db.client import supabase
from src.config.settings import settings
import jwt

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Verify JWT using the project secret
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], audience="authenticated")
        user_id = payload.get("sub")
        if user_id is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"id": user_id, "email": payload.get("email")}
    except jwt.PyJWTError:
        # Fallback: Validation via Supabase client (slower but more robust if needed)
        try:
            user = supabase.auth.get_user(token)
            if not user:
                 raise HTTPException(status_code=401, detail="Invalid token")
            return {"id": user.user.id, "email": user.user.email}
        except Exception:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
