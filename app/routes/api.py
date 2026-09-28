import json,uuid
from pathlib import Path
from fastapi import APIRouter,Depends,File,Form,HTTPException,UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..ai.gemini_service import gemini_service
from ..auth import COOKIE_NAME,create_access_token,hash_password,verify_password
from ..config import settings
from ..database import get_db
from ..dependencies import get_current_user
from ..models import RecommendationHistory,User
from ..schemas import HomeRequest,LoginRequest,PartyRequest,RecommendationResponse,RegisterRequest
router=APIRouter(prefix="/api"); Path("uploads").mkdir(exist_ok=True)
ALLOWED={"image/jpeg","image/png","image/webp"}

def save_history(db,user,planner,budget,data,result,ai_powered):
    result["ai_powered"]=ai_powered
    result["source_note"]=("Gemini-generated suggestions with marketplace search links. Verify current price, stock, seller, delivery and return policy before purchase." if ai_powered else "Local fallback recommendations are shown because Gemini is unavailable or not configured.")
    row=RecommendationHistory(user_id=user.id,planner=planner,budget=budget,input_summary=json.dumps(data),result_json=json.dumps(result))
    db.add(row); db.commit(); db.refresh(row); result["history_id"]=row.id; return result

@router.get("/health")
def health(): return {"status":"ok","service":settings.app_name,"gemini_configured":bool(settings.gemini_api_key),"model":settings.gemini_model}

@router.post("/register")
def register(payload:RegisterRequest,db:Session=Depends(get_db)):
    username=payload.username.strip(); email=payload.email.lower().strip()
    if db.query(User).filter(User.email==email).first(): raise HTTPException(409,"Email already registered")
    if db.query(User).filter(User.username==username).first(): raise HTTPException(409,"Username already registered")
    user=User(username=username,email=email,password_hash=hash_password(payload.password)); db.add(user); db.commit(); db.refresh(user)
    token=create_access_token(user.id); out=JSONResponse({"message":"Registration successful","user":{"id":user.id,"username":user.username}})
    out.set_cookie(COOKIE_NAME,token,httponly=True,samesite="lax",secure=False,max_age=43200); return out

@router.post("/login")
def login(payload:LoginRequest,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password,user.password_hash): raise HTTPException(401,"Invalid email or password")
    out=JSONResponse({"message":"Login successful","user":{"id":user.id,"username":user.username}})
    out.set_cookie(COOKIE_NAME,create_access_token(user.id),httponly=True,samesite="lax",secure=False,max_age=43200); return out

@router.post("/logout")
def logout():
    out=JSONResponse({"message":"Logged out"}); out.delete_cookie(COOKIE_NAME); return out

@router.get("/session-info")
def session_info(user:User=Depends(get_current_user)): return {"logged_in":True,"user_id":user.id,"username":user.username,"email":user.email}

@router.get("/session-data")
def session_data(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return {"user_id":user.id,"recommendation_count":db.query(RecommendationHistory).filter(RecommendationHistory.user_id==user.id).count()}

@router.post("/generate-home",response_model=RecommendationResponse)
def home(payload:HomeRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    data=payload.model_dump(); result,ai=gemini_service.recommend("home",data); return save_history(db,user,"home",payload.budget,data,result,ai)

@router.post("/generate-party",response_model=RecommendationResponse)
def party(payload:PartyRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    data=payload.model_dump(); result,ai=gemini_service.recommend("party",data); return save_history(db,user,"party",payload.budget,data,result,ai)

@router.post("/generate-jewelry",response_model=RecommendationResponse)
async def jewelry(budget:int=Form(...),occasion:str=Form(...),style:str=Form("classic"),notes:str=Form(""),outfit_image:UploadFile|None=File(None),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    image=None; mime=None
    if outfit_image and outfit_image.filename:
        if outfit_image.content_type not in ALLOWED: raise HTTPException(415,"Only JPG, PNG and WEBP images are supported")
        image=await outfit_image.read()
        if len(image)>settings.max_upload_mb*1024*1024: raise HTTPException(413,f"Image must be <= {settings.max_upload_mb} MB")
        try:
            from PIL import Image
            from io import BytesIO
            with Image.open(BytesIO(image)) as im: im.verify()
        except Exception: raise HTTPException(400,"Uploaded file is not a valid image")
        (Path("uploads")/f"{uuid.uuid4().hex}.bin").write_bytes(image); mime=outfit_image.content_type
    data={"budget":budget,"occasion":occasion.strip(),"style":style.strip(),"notes":notes.strip()}
    result,ai=gemini_service.recommend("jewelry",data,image,mime); return save_history(db,user,"jewelry",budget,data,result,ai)

@router.get("/history")
def history(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.query(RecommendationHistory).filter(RecommendationHistory.user_id==user.id).order_by(RecommendationHistory.created_at.desc()).limit(50).all()
    return [{"id":r.id,"planner":r.planner,"budget":r.budget,"created_at":r.created_at.isoformat() if r.created_at else None,"result":json.loads(r.result_json)} for r in rows]

@router.get("/recommendations/{history_id}",response_model=RecommendationResponse)
def recommendation(history_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    row=db.query(RecommendationHistory).filter(RecommendationHistory.id==history_id,RecommendationHistory.user_id==user.id).first()
    if not row: raise HTTPException(404,"Recommendation not found")
    result=json.loads(row.result_json); result["history_id"]=row.id; return result
