from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from loguru import logger
from models import User, UserCarmine
from base.security import create_user_token
from fastapi import Request
from base.security import UserContext
from fastapi import Depends
router = APIRouter()

class LoginResponse(BaseModel):
    token: str
    user_id: int
    username: str
    expires_at: datetime

class RegisterRequest(BaseModel):
    username: str
    password: str
    carmine: str

class HeartbeatResponse(BaseModel):
    status: str
    user_id: int
    username: str
    expires_at: datetime

@router.post("/user/login")
async def login(username: str, password: str):
    """
    用户登录
    """
    logger.info(f"用户登录: username={username}")
    
    try:
        user = User.get(User.username == username)
    except User.DoesNotExist:
        logger.error(f"用户不存在: {username}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.password != password:  # 实际应用中应使用加密密码
        logger.error(f"密码错误: username={username}")
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 查找用户的有效卡密
    now = datetime.now()
    valid_carmine = None
    
    try:
        valid_carmine = UserCarmine.select().where(
            (UserCarmine.user_id == user.id) & 
            (UserCarmine.activated_at.is_null(False)) & 
            ((UserCarmine.expired_at > now) | (UserCarmine.expired_at.is_null()))
        ).order_by(UserCarmine.expired_at.desc()).get()
    except UserCarmine.DoesNotExist:
        logger.warning(f"用户没有有效卡密: user_id={user.id}")
        raise HTTPException(status_code=403, detail="您的账号已过期，请续费")
    
    # 生成token
    token = create_user_token(user.id)
    
    logger.info(f"用户登录成功: username={username}, user_id={user.id}")
    return LoginResponse(
        token=token,
        user_id=user.id,
        username=user.username,
        expires_at=valid_carmine.expired_at
    )
@router.post("/user/register")
async def register(request: RegisterRequest, request_header: Request):
    """
    用户注册
    """
    # 从请求头获取MAC地址
    mac = request_header.headers.get("mac")
    if not mac:
        logger.error(f"请求头中缺少MAC地址")
        raise HTTPException(status_code=400, detail="请求头中缺少MAC地址")
    
    logger.info(f"用户注册: username={request.username}, carmine={request.carmine}, mac={mac}")
    
    # 检查用户名是否已存在
    if User.select().where(User.username == request.username).exists():
        logger.error(f"用户名已存在: {request.username}")
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 验证卡密
    try:
        carmine = UserCarmine.get(UserCarmine.carmine == request.carmine)
    except UserCarmine.DoesNotExist:
        logger.error(f"卡密不存在: {request.carmine}")
        raise HTTPException(status_code=404, detail="卡密不存在")
    
    # 检查卡密是否已激活
    if carmine.activated_at is not None:
        logger.error(f"卡密已被使用: {request.carmine}")
        raise HTTPException(status_code=400, detail="卡密已被使用")
    
    # 创建用户
    user = User(
        username=request.username,
        password=request.password,  # 实际应用中应加密存储
        mac=mac,
    )
    user.save()
    
    # 激活卡密
    now = datetime.now()
    expired_at = now + timedelta(days=carmine.duration)
    
    carmine.user = user
    carmine.activated_at = now
    carmine.expired_at = expired_at
    carmine.save()
    
    # 生成token
    token = create_user_token(user.id)
    
    logger.info(f"用户注册成功: username={request.username}, user_id={user.id}, mac={mac}")
    return LoginResponse(
        token=token,
        user_id=user.id,
        username=user.username,
        expires_at=expired_at
    )

@router.get("/user/heartbeat")
async def heartbeat(user_ctx: UserContext = Depends(UserContext)):
    """
    用户心跳接口，用于验证用户登录状态和会员有效期
    """
    logger.info(f"用户心跳: user_id={user_ctx.user_id}")
    
    # 查找用户的有效卡密
    now = datetime.now()
    valid_carmine = None
    
    try:
        valid_carmine = UserCarmine.select().where(
            (UserCarmine.user_id == user_ctx.user_id) & 
            (UserCarmine.activated_at.is_null(False)) & 
            ((UserCarmine.expired_at > now) | (UserCarmine.expired_at.is_null()))
        ).order_by(UserCarmine.expired_at.desc()).get()
    except UserCarmine.DoesNotExist:
        logger.warning(f"用户没有有效卡密: user_id={user_ctx.user_id}")
        raise HTTPException(status_code=403, detail="您的账号已过期，请续费")
    
    logger.info(f"用户心跳成功: user_id={user_ctx.user_id}")
    return HeartbeatResponse(
        status="ok",
        user_id=user_ctx.user_id,
        username=user_ctx.user.username,
        expires_at=valid_carmine.expired_at
    )
