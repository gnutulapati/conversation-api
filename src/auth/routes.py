from fastapi import APIRouter, HTTPException, status, Depends
from src.auth.schemas import UserRegister, UserLogin, Token
from src.db.client import supabase
from gotrue.errors import AuthApiError

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    try:
        res = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })
        if not res.user:
            raise HTTPException(status_code=400, detail="Registration failed")
            
        return {
            "access_token": res.session.access_token if res.session else "pending_verification",
            "token_type": "bearer",
            "refresh_token": res.session.refresh_token if res.session else None,
            "user": {"id": res.user.id, "email": res.user.email}
        }
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password,
        })
        return {
            "access_token": res.session.access_token,
            "token_type": "bearer",
            "refresh_token": res.session.refresh_token,
            "user": {"id": res.user.id, "email": res.user.email}
        }
    except AuthApiError as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@router.post("/logout")
async def logout(token: str = Depends(lambda x: x)): # Placeholder, usually handled on client side by discarding token
    # Supabase logout invalidates the session
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
